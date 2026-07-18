from pydantic import BaseModel

class UserProfileBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None

class UserProfileRequest(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    class Config:
        from_attributes = True
