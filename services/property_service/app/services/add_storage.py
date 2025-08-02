from app.dto.storage import PropertyStorageRequest, PropertyStorageResponse
from app.models.storage import Storage


class AddStorage:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def add_storage(self, storage_request: PropertyStorageRequest) -> PropertyStorageResponse:
        self.logger.info(f"Adding sub-storage '{storage_request.storage_name}' under container {storage_request.container_id}")
        
        # Validate that container_id is provided for sub-storage
        if storage_request.container_id is None:
            error_msg = "Sub-storage must have a container_id. Use AddMainStorage for main storage containers."
            self.logger.error(error_msg)
            return PropertyStorageResponse(message=error_msg)
        
        # Validate storage_name is provided
        if not storage_request.storage_name or not storage_request.storage_name.strip():
            error_msg = "Storage name is required"
            self.logger.error(error_msg)
            return PropertyStorageResponse(message=error_msg)
        
        # Validate that parent storage exists
        parent_storage = self.session.query(Storage).filter(
            Storage.id == storage_request.container_id,
            Storage.property_id == storage_request.property_id,
            Storage.room_id == storage_request.room_id
        ).first()
        
        if not parent_storage:
            error_msg = f"Container with ID {storage_request.container_id} not found in room {storage_request.room_id}"
            self.logger.error(error_msg)
            return PropertyStorageResponse(message=error_msg)
        
        storage = Storage(
            property_id=storage_request.property_id,
            room_id=storage_request.room_id,
            container_id=storage_request.container_id,
            storage_name=storage_request.storage_name.strip()
        )

        try:
            self.session.add(storage)
            self.session.flush()
            self.session.commit()

            success_msg = f"Sub-storage '{storage.storage_name}' added successfully with ID {storage.id} under container '{parent_storage.storage_name}'"
            self.logger.info(success_msg)
            return PropertyStorageResponse(message=success_msg)

        except Exception as e:
            error_msg = f"Failed to add sub-storage: {str(e)}"
            self.logger.error(error_msg)
            self.session.rollback()
            return PropertyStorageResponse(message=error_msg)
