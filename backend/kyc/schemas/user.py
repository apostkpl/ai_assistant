import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from kyc.schemas.user_profile import UserProfileResponse, UserProfileRequest
from kyc.schemas.user_address import UserAddressResponse

class UserBase(BaseModel):
    email: EmailStr

class UserRequest(UserBase):
    password: str = Field(..., min_length=8)
    profile: UserProfileRequest | None = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one numeric digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_]", value):
            raise ValueError("Password must contain at least one special character.")
        return value

class UserResponse(UserBase):
    public_id: str
    is_active: bool
    is_subscribed: bool
    created_at: datetime
    profile: UserProfileResponse | None = None
    addresses: list[UserAddressResponse] = []

    class Config:
        from_attributes = True

class EmailVerificationRequest(BaseModel):
    token: str = Field(..., description="JWT token for email verification")
