from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .data_base import DataBaseModel


class User(DataBaseModel):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(64))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    items = relationship("Item", back_populates="owner")


class RefreshToken(DataBaseModel):
    __tablename__ = "refresh_tokens"

    jti = Column(String(36), primary_key=True, index=True)
    public_id = Column(String(36), index=True)
    is_blacklisted = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=False), default=func.now())


class Item(DataBaseModel):
    __tablename__ = "items"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
