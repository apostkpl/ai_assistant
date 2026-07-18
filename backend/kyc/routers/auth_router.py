from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from kyc.core.database import get_db
from kyc.core.security import create_email_verification_token
from kyc.core.email import send_verification_email
from kyc.schemas.user import UserRequest, UserResponse, EmailVerificationRequest
from kyc.schemas.token import Token
from kyc.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(request: UserRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_user = AuthService.create_user(db=db, request=request)
    token = create_email_verification_token(new_user.email) #type: ignore
    background_tasks.add_task(send_verification_email, new_user.email, token) #type: ignore
    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a signed JWT access token.
    Complies with OAuth2 specification for Swagger UI integration.
    """
    return AuthService.authenticate_user(
        db=db,
        email=form_data.username,  # The standard OAuth2 spec always calls this 'username'
        plain_password=form_data.password
    )

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Consumes the email verification token to activate the user account.
    Expects a JSON payload: {"token": "eyJhbG..."}
    """
    AuthService.verify_email(db=db, token=request.token)
    return {"message": "Email successfully verified. You may now log in."}
