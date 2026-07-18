from fastapi import APIRouter, Depends
from kyc.schemas.user import UserResponse
from kyc.models.user import User
from kyc.core.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Returns the profile and status of the currently authenticated user.
    """
    return current_user