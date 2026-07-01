from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.backend.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="inspector")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())