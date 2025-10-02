# app/models/user.py (Example)
from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.db import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Add relationships to Wallets, etc. here