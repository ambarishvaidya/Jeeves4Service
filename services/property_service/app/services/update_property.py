from services.property_service.app.dto.property import UpdatePropertyRequest, PropertyResponse
from services.property_service.app.models.property import Property
from sqlalchemy.orm.exc import NoResultFound


class UpdateProperty:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def update_property(self, update_request: UpdatePropertyRequest) -> PropertyResponse:
        self.logger.info(f"Updating property with ID: {update_request.property_id}")
        
        try:
            # Find the property
            property_obj = self.session.query(Property).filter(
                Property.id == update_request.property_id
            ).first()
            
            if not property_obj:
                raise ValueError(f"Property with ID {update_request.property_id} not found")
            
            # Update fields if provided
            updated_fields = []
            if update_request.name is not None:
                property_obj.name = update_request.name
                updated_fields.append("name")
            
            if update_request.address is not None:
                property_obj.address = update_request.address
                updated_fields.append("address")
            
            if not updated_fields:
                return PropertyResponse(
                    message="No fields provided for update"
                )
            
            self.session.commit()
            
            self.logger.info(f"Property {property_obj.id} updated successfully. Fields updated: {', '.join(updated_fields)}")
            return PropertyResponse(
                message=f"Property '{property_obj.name}' updated successfully. Updated fields: {', '.join(updated_fields)}"
            )

        except Exception as e:
            response = PropertyResponse(
                message=f"Failed to update property: {str(e)}"
            )
            self.logger.error(f"Error updating property: {str(e)}")
            self.session.rollback()
            raise e
        
        finally:
            if self.session:
                self.session.close()
