from pydantic import BaseModel

class UserAddressBase(BaseModel):
    address_line1: str
    address_line2: str | None = None
    city: str
    postal_code: str
    country: str

class UserAddressRequest(UserAddressBase):
    pass

class UserAddressResponse(UserAddressBase):
    id: int

    class Config:
        from_attributes = True
