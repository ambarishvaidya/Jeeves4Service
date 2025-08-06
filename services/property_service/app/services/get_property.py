from typing import final

from services.property_service.app.dto.property import PropertyResponse
from services.property_service.app.models.property import Property, PropertyAssociation


class GetProperty:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session

    def get_properties(self, user_id: int) -> list:
        try:
            self.logger.info(f"Fetching properties for user ID {user_id}")
            properties = self.session.query(Property).join(
                PropertyAssociation
            ).filter(PropertyAssociation.user_id == user_id).all()
            self.logger.info(f"Found {len(properties)} properties for user ID {user_id}")
            return [PropertyResponse(id=property.id, name=property.name, address=property.address) for property in properties]
                    
        except Exception as e:
            self.logger.error(f"Error fetching properties for user ID {user_id}: {e}")            
            return []
        
        finally:
            if self.session:
                self.session.close()

    def get_property_by_id(self, property_id: int) -> PropertyResponse:
        try:
            self.logger.info(f"Fetching property with ID {property_id}")
            property = self.session.query(Property).filter(Property.id == property_id).first()
            if property:
                self.logger.info(f"Found property: {property.name} with ID {property.id}")
            else:
                self.logger.warning(f"No property found with ID {property_id}")
            return PropertyResponse(id=property.id, name=property.name, address=property.address) if property else None
        
        except Exception as e:
            self.logger.error(f"Error fetching property with ID {property_id}: {e}")
            return None
        finally:
            if self.session:
                self.session.close()
