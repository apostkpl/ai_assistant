from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from kyc.core.database import Base

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), nullable=False)

    user = relationship("User", back_populates="addresses")
