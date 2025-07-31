from math import floor
from sqlalchemy import Column, ForeignKey, Integer, String, null

from app.db.base import Base

# Simple table that currently just holds the property and who created it.
# Name is what will be used to identify the property. We are not as of
# now interested in the other details.
class Property(Base):
    __tablename__ = "location"
    __table_args__ = {"schema": "property"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, index=True)
    created_by = Column(Integer, nullable=True)

# These could be areas instead of rooms. The expected nomenclaure is 
# ground floor first room, or main living room or main kitchen or 
# dry balcony or main balcony. 
class PropertyRooms(Base):
    __tablename__ = "rooms"
    __table_args__ = {"schema": "property"}

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.location.id"), nullable=False)
    room_name = Column(String, index=True, nullable=False)    
    
# This is how a property is associated with a user. A user can be associated
# with multiple properties. This is a many to many relationship.
class PropertyAssociation(Base):
    __tablename__ = "associations"
    __table_args__ = {"schema": "property"}

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.location.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
        