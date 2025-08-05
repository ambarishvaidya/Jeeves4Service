from services.property_service.app.dto.property import NewPropertyRequest, PropertyResponse
from services.property_service.app.models.property import Property, PropertyAssociation



class AddProperty:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def add_property(self, new_property: NewPropertyRequest) -> PropertyResponse:
        self.logger.info("Adding new property")
        
        property = Property(
            name=new_property.name,
            address=new_property.address,
            created_by=new_property.created_by
        )

        try:
            self.session.add(property)
            self.session.flush()

            property_user = PropertyAssociation(
                        property_id=property.id,
                        user_id=new_property.created_by
                    ) 

            self.session.add(property_user)
            self.session.commit()

            return PropertyResponse(
                message=f"Property '{property.name}' added successfully with ID {property.id}"
            )

        except Exception as e:
            response = PropertyResponse(
                message=f"Failed to add property: {str(e)}"
            )
            self.logger.error(f"Error adding property: {str(e)}")
            self.session.rollback()
            raise e
        
        finally:
            if self.session:
                self.session.close()
