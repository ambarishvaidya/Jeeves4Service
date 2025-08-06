from typing import List

from services.property_service.app.dto.storage import PropertyStorageResponse
from services.property_service.app.models.storage import Storage
from services.property_service.app.models.property import PropertyAssociation


class GetStorage:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session

    def get_storage_by_property(self, property_id: int) -> List[PropertyStorageResponse]:
        """Get all storage for a specific property"""
        try:
            self.logger.info(f"Fetching storage for property ID {property_id}")
            storage_items = self.session.query(Storage).filter(
                Storage.property_id == property_id
            ).all()
            self.logger.info(f"Found {len(storage_items)} storage items for property ID {property_id}")
            return [
                PropertyStorageResponse(
                    id=storage.id,
                    property_id=storage.property_id,
                    room_id=storage.room_id,
                    container_id=storage.container_id,
                    storage_name=storage.storage_name
                ) for storage in storage_items
            ]
                    
        except Exception as e:
            self.logger.error(f"Error fetching storage for property ID {property_id}: {e}")            
            return []
        
        finally:
            if self.session:
                self.session.close()

    def get_storage_by_room(self, room_id: int) -> List[PropertyStorageResponse]:
        """Get all storage for a specific room"""
        try:
            self.logger.info(f"Fetching storage for room ID {room_id}")
            storage_items = self.session.query(Storage).filter(
                Storage.room_id == room_id
            ).all()
            self.logger.info(f"Found {len(storage_items)} storage items for room ID {room_id}")
            return [
                PropertyStorageResponse(
                    id=storage.id,
                    property_id=storage.property_id,
                    room_id=storage.room_id,
                    container_id=storage.container_id,
                    storage_name=storage.storage_name
                ) for storage in storage_items
            ]
                    
        except Exception as e:
            self.logger.error(f"Error fetching storage for room ID {room_id}: {e}")            
            return []
        
        finally:
            if self.session:
                self.session.close()

    def get_storage_by_id(self, storage_id: int) -> PropertyStorageResponse:
        """Get a specific storage by its ID"""
        try:
            self.logger.info(f"Fetching storage with ID {storage_id}")
            storage = self.session.query(Storage).filter(Storage.id == storage_id).first()
            if storage:
                self.logger.info(f"Found storage: {storage.storage_name} with ID {storage.id}")
                return PropertyStorageResponse(
                    id=storage.id,
                    property_id=storage.property_id,
                    room_id=storage.room_id,
                    container_id=storage.container_id,
                    storage_name=storage.storage_name
                )
            else:
                self.logger.warning(f"No storage found with ID {storage_id}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error fetching storage with ID {storage_id}: {e}")
            return None
        finally:
            if self.session:
                self.session.close()