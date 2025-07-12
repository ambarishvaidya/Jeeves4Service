from sqlalchemy import Column, Integer, LargeBinary, Date, Boolean
from sqlalchemy.orm import Mapped
from app.db.base import Base
from datetime import date

class Family(Base):
    __tablename__ = "family"
    """
    Admin in family can add new users to the family.
    """
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    family_uuid: Mapped[bytes] = Column(LargeBinary, nullable=False, unique=False)
    user_id: Mapped[int] = Column(Integer, nullable=False)
    user_added: Mapped[date] = Column(Date, nullable=False, default=date.today)
    is_admin: Mapped[bool] = Column(Boolean, default=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)