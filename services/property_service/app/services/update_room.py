from services.property_service.app.dto.property import UpdateRoomRequest, RoomResponse
from services.property_service.app.models.property import PropertyRooms
from sqlalchemy import and_


class UpdateRoom:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def update_room(self, request: UpdateRoomRequest) -> RoomResponse:
        self.logger.info(f"Updating room {request.room_id} to name '{request.room_name}'")
        
        try:
            # Find the room
            room = self.session.query(PropertyRooms).filter(
                PropertyRooms.id == request.room_id
            ).first()
            
            if not room:
                raise ValueError(f"Room with ID {request.room_id} not found")
            
            # Check if the new room name already exists for this property (excluding current room)
            existing_room = self.session.query(PropertyRooms).filter(
                and_(
                    PropertyRooms.property_id == room.property_id,
                    PropertyRooms.room_name == request.room_name,
                    PropertyRooms.id != request.room_id
                )
            ).first()
            
            if existing_room:
                raise ValueError(f"Room name '{request.room_name}' already exists in this property")
            
            # Check if the name is actually changing
            if room.room_name == request.room_name:
                return RoomResponse(
                    message=f"Room name is already '{request.room_name}'. No update needed.",
                    room_id=room.id
                )
            
            old_name = room.room_name
            room.room_name = request.room_name
            
            self.session.commit()
            
            self.logger.info(f"Room {request.room_id} updated successfully from '{old_name}' to '{request.room_name}'")
            return RoomResponse(
                message=f"Room name updated successfully from '{old_name}' to '{request.room_name}'",
                room_id=room.id
            )

        except Exception as e:
            self.logger.error(f"Error updating room: {str(e)}")
            self.session.rollback()
            raise e
