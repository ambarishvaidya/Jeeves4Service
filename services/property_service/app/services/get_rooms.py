from typing import List

from services.property_service.app.dto.property import RoomResponse
from services.property_service.app.models.property import PropertyRooms, PropertyAssociation


class GetRooms:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session

    def get_rooms_by_property(self, property_id: int) -> List[RoomResponse]:
        """Get all rooms for a specific property"""
        try:
            self.logger.info(f"Fetching rooms for property ID {property_id}")
            rooms = self.session.query(PropertyRooms).filter(
                PropertyRooms.property_id == property_id
            ).all()
            self.logger.info(f"Found {len(rooms)} rooms for property ID {property_id}")
            return [
                RoomResponse(
                    id=room.id, 
                    property_id=room.property_id, 
                    room_name=room.room_name
                ) for room in rooms
            ]
                    
        except Exception as e:
            self.logger.error(f"Error fetching rooms for property ID {property_id}: {e}")            
            return []
        
        finally:
            if self.session:
                self.session.close()

    def get_room_by_id(self, room_id: int) -> RoomResponse:
        """Get a specific room by its ID"""
        try:
            self.logger.info(f"Fetching room with ID {room_id}")
            room = self.session.query(PropertyRooms).filter(PropertyRooms.id == room_id).first()
            if room:
                self.logger.info(f"Found room: {room.room_name} with ID {room.id}")
                return RoomResponse(
                    id=room.id, 
                    property_id=room.property_id, 
                    room_name=room.room_name
                )
            else:
                self.logger.warning(f"No room found with ID {room_id}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error fetching room with ID {room_id}: {e}")
            return None
        finally:
            if self.session:
                self.session.close()
