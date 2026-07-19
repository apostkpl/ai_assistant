
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from kyc.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # State control flags
    is_active = Column(Boolean, default=False, nullable=False)
    is_subscribed = Column(Boolean, default=False, nullable=False)

    # Audit trail fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    # Relationship with other tables
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")

    # toString() override
    def __repr__(self) -> str:
        return f"<User email={self.email} subscribed={self.is_subscribed}> created_at={self.created_at}"
