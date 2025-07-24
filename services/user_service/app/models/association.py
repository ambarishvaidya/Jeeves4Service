from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from app.db.base import Base


class PropertyAssociation(Base):
    __tablename__ = "property_association"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id: Mapped[int] = Column(Integer, nullable=False)
    