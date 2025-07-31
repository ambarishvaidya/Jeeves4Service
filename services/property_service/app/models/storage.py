from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.base import Base

# Assuming that there is a master bedroom with id as 3then the following will be defined 
# as storage. Assuming property_id as 1 and room_id as 3, then the storage_id will be
# 23, 1, 3, null, left_wardrobe
# 24, 1, 3, 23, top shelf
# 25, 1, 3, 24, black right container
# so the main storage will have stoage id as null.
# items will be stored to the storage_id. Its 
# location will be traced back from storage_id
class Storage(Base):
    __tablename__ = "storage"
    __table_args__ = {'schema': "property"}

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.details.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("property.rooms.id"), nullable=False)
    storage_id = Column(Integer, nullable=True)
    storage_name = Column(String, index=True, nullable=False)    
    
