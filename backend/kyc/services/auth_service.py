import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from kyc.models.user import User
from kyc.models.user_profile import UserProfile
from kyc.schemas.user import UserRequest
from kyc.schemas.token import Token
from kyc.core.security import hash_password, verify_password, create_access_token, verify_email_token

logger = logging.getLogger(__name__)

class AuthService:

    @staticmethod
    def create_user(db: Session, request: UserRequest) -> User:
        """Handles user registration and nests the profile initialization."""
        logger.debug(f"Starting registration process for email: {request.email}")
        # 1. Check if email is already taken
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            logger.warning(f"Registration failed: Email {request.email} is already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # 2. Hash password and build the core User entity
        new_user = User(
            email=request.email,
            hashed_password=hash_password(request.password)
        )

        # 3. If profile data was passed in the request, map it to the UserProfile entity
        if request.profile:
            logger.debug(f"Profile data received for profile: {request.profile}")
            new_profile = UserProfile(
                first_name=request.profile.first_name,
                last_name=request.profile.last_name,
                phone_number=request.profile.phone_number
            )
            new_user.profile = new_profile

        # 4. Commit to database
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Successfully registered user {request.email} with ID: {new_user.public_id}")
            return new_user
        except IntegrityError as e:
            # Catches race conditions where someone else registers the exact same email
            db.rollback()
            logger.warning(f"Database integrity constraint violated for {request.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A conflict occurred during registration."
            )
        except SQLAlchemyError as e:
            # Catches DB failures (eg connection errors, deadlocks)
            db.rollback()
            logger.error(f"Critical database error during registration for {request.email}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred."
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during registration for {request.email}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred."
            )

    @staticmethod
    def authenticate_user(db: Session, email: str, plain_password: str) -> Token:
        """Validates credentials and generates an access token."""
        logger.debug(f"Authentication attempt for email: {email}")
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(plain_password, user.hashed_password): #type: ignore
            logger.warning(f"Failed login attempt for {email}: Invalid credentials.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active: #type: ignore
            logger.warning(f"Blocked login attempt for {email}: Account deactivated.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account has been deactivated"
            )

        # Generate the JWT payload
        token_payload = {"sub": user.email, "id": user.id, "public_id": user.public_id}
        access_token = create_access_token(data=token_payload)

        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        """Validates the token and activates the corresponding user account."""
        logger.debug("Processing email verification token.")

        # 1. Decode token and extract email
        user_email = verify_email_token(token)

        # 2. Fetch the corresponding user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            logger.warning(f"Verification failed: No user found matching email {user_email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.is_active:  # type: ignore
            logger.info(f"User {user_email} attempted to verify but is already active.")
            return True

        # 3. Transaction Block to update status
        try:
            user.is_active = True  # type: ignore
            db.commit()
            logger.info(f"User account {user_email} successfully activated.")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database failure while activating user {user_email}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating account status."
            )
        except Exception as e:
            logger.error(f"Unexpected error during email verification: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while verifying email."
            )
