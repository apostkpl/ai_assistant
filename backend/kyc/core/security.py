import logging
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import HTTPException, status
from kyc.config.settings import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Catastrophic failure during password hashing. Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during security operations."
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its database hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error during password verification (potential hash corruption). Error: {e}", exc_info=True)
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generates a cryptographically signed JSON Web Token (JWT).
    """
    user_email = data.get("sub", "Unknown")
    logger.debug(f"Generating access token for user: {user_email}")

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.app.token_expire_minutes)

    to_encode.update({"exp": int(expire.timestamp())})

    try:
        encoded_jwt = jwt.encode(to_encode, settings.app.secret_key, algorithm=ALGORITHM)
        logger.debug(f"Successfully generated and signed JWT for user: {user_email}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Critical failure signing JWT for user: {user_email}. Check secret key. Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate access token."
        )

def create_email_verification_token(email: str) -> str:
    """Generates a short-lived token (e.g., 24 hours) for email verification."""
    logger.debug(f"Generating email verification token for: {email}")
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": email,
        "exp": int(expire.timestamp()),
        "purpose": "email_verification"
    }
    try:
        return jwt.encode(payload, settings.app.secret_key, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Failed to generate verification token for {email}. Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating verification token."
        )

def verify_email_token(token: str) -> str:
    """Decodes and validates the email verification token, returning the user email."""
    try:
        payload = jwt.decode(token, settings.app.secret_key, algorithms=[ALGORITHM])

        # Verify purpose so a login token can't be used to verify an email
        if payload.get("purpose") != "email_verification":
            logger.warning("Token verification failed: Invalid purpose claim.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")

        user_email = payload.get("sub")
        if not user_email:
            logger.warning(f"Token verification failed for user {user_email}: Invalid token payload.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload.")

        return user_email

    except jwt.ExpiredSignatureError:
        logger.warning("Email verification failed: Token has expired.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link has expired.")
    except jwt.PyJWTError as e:
        logger.warning(f"Email verification failed: Invalid token signature. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification link.")
