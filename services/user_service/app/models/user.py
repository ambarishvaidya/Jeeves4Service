from sqlalchemy import Column, Integer, String, LargeBinary, Date, Boolean, UUID
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
