from ast import Add
from math import log
from services.property_service.app.dto.storage import PropertyStorageRequest, PropertyStorageResponse
from services.property_service.app.models.property import Property, PropertyRooms
from services.property_service.app.models.storage import LocationPath, Storage



class AddMainStorage:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def add_main_storage(self, storage_request: PropertyStorageRequest) -> PropertyStorageResponse:
        self.logger.info(f"Adding main storage '{storage_request.storage_name}' to room {storage_request.room_id}")
        
        # Validate that container_id is None for main storage
        if storage_request.container_id is not None:
            error_msg = "Main storage should not have a container_id. Use AddStorage for sub-storage."
            self.logger.error(error_msg)
            return PropertyStorageResponse(message=error_msg)
        
        # Validate storage_name is provided
        if not storage_request.storage_name or not storage_request.storage_name.strip():
            error_msg = "Storage name is required"
            self.logger.error(error_msg)
            return PropertyStorageResponse(message=error_msg)
        
        storage = Storage(
            property_id=storage_request.property_id,
            room_id=storage_request.room_id,
            container_id=None,  # Main storage has no parent
            storage_name=storage_request.storage_name.strip()
        )

        property = self.session.query(Property).filter(Property.id == storage_request.property_id).first()
        room = self.session.query(PropertyRooms).filter(PropertyRooms.id == storage_request.room_id).first()
        path = f"{property.name} : {room.room_name} : {storage.storage_name}"
        self.logger.info(f"Location path for main storage: {path}")
        

        try:
            self.session.add(storage)
            self.session.flush()

            location = LocationPath(
                property_id=property.id,
                storage_id=storage.id,
                location_path=path
            )
            self.logger.info(f"Adding location path: {location}")
            self.session.add(location)
            self.session.flush()
            self.session.commit()

            success_msg = f"Main storage '{storage.storage_name}' added successfully with ID {storage.id}"
            self.logger.info(success_msg)
            return PropertyStorageResponse(message=success_msg)

        except Exception as e:
            error_msg = f"Failed to add main storage: {str(e)}"
            self.logger.error(error_msg)
            self.session.rollback()
            return PropertyStorageResponse(message=error_msg)
        
        finally:
            if self.session:
                self.session.close()
