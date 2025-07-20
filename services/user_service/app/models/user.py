import email
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary, Date, Boolean, UUID
from datetime import date
from sqlalchemy.orm import Mapped
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = Column(String(50), nullable=False)
    last_name: Mapped[str] = Column(String(50), nullable=False)
    email: Mapped[str] = Column(String(100), unique=True, nullable=False)
    password_hash: Mapped[bytes] = Column(LargeBinary, nullable=False)
    salt: Mapped[bytes] = Column(LargeBinary, nullable=False)
    dob: Mapped[date] = Column(Date, nullable=True)
    is_admin: Mapped[bool] = Column(Boolean, default=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)


'''
This class represents a user in the system, with fields for personal information, authentication, and status.
This is only for testing purposes.'''
class UserPassword(Base):
    __tablename__ = "user_passwords"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = Column(String(100), nullable=False)
    password_str: Mapped[str] = Column(String(100), nullable=False)