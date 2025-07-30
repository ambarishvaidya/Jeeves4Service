from app.dto.property import PropertyRoomRequest, RoomResponse
from app.models.property import Property, PropertyRooms
from sqlalchemy import and_


class AddRooms:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def add_room(self, request: PropertyRoomRequest) -> RoomResponse:
        self.logger.info(f"Adding room '{request.room_name}' to property {request.property_id}")
        
        try:
            # Verify property exists
            property_obj = self.session.query(Property).filter(
                Property.id == request.property_id
            ).first()
            
            if not property_obj:
                raise ValueError(f"Property with ID {request.property_id} not found")
            
            # Check if room name already exists for this property
            existing_room = self.session.query(PropertyRooms).filter(
                and_(
                    PropertyRooms.property_id == request.property_id,
                    PropertyRooms.room_name == request.room_name
                )
            ).first()
            
            if existing_room:
                raise ValueError(f"Room '{request.room_name}' already exists in property '{property_obj.name}'")
            
            # Create new room
            new_room = PropertyRooms(
                property_id=request.property_id,
                room_name=request.room_name
            )
            
            self.session.add(new_room)
            self.session.flush()  # To get the ID
            self.session.commit()
            
            self.logger.info(f"Room '{request.room_name}' added successfully to property {request.property_id} with ID {new_room.id}")
            return RoomResponse(
                message=f"Room '{request.room_name}' added successfully to property '{property_obj.name}'",
                room_id=new_room.id
            )

        except Exception as e:
            self.logger.error(f"Error adding room: {str(e)}")
            self.session.rollback()
            raise e
