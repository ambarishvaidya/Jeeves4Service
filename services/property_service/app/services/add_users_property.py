from app.dto.property import AddUsersPropertyRequest, PropertyResponse
from app.models.property import Property, PropertyAssociation
from sqlalchemy import and_


class AddUsersProperty:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session        

    def add_users_to_property(self, request: AddUsersPropertyRequest) -> PropertyResponse:
        self.logger.info(f"Adding users {request.user_ids} to property {request.property_id}")
        
        try:
            # Verify property exists
            property_obj = self.session.query(Property).filter(
                Property.id == request.property_id
            ).first()
            
            if not property_obj:
                raise ValueError(f"Property with ID {request.property_id} not found")
            
            # Check for existing associations
            existing_associations = self.session.query(PropertyAssociation).filter(
                and_(
                    PropertyAssociation.property_id == request.property_id,
                    PropertyAssociation.user_id.in_(request.user_ids)
                )
            ).all()
            
            existing_user_ids = {assoc.user_id for assoc in existing_associations}
            new_user_ids = [user_id for user_id in request.user_ids if user_id not in existing_user_ids]
            
            if not new_user_ids:
                return PropertyResponse(
                    message=f"All specified users are already associated with property '{property_obj.name}'"
                )
            
            # Create new associations
            new_associations = []
            for user_id in new_user_ids:
                association = PropertyAssociation(
                    property_id=request.property_id,
                    user_id=user_id
                )
                new_associations.append(association)
                self.session.add(association)
            
            self.session.commit()
            
            skipped_count = len(request.user_ids) - len(new_user_ids)
            message = f"Added {len(new_user_ids)} users to property '{property_obj.name}'"
            if skipped_count > 0:
                message += f" ({skipped_count} users were already associated)"
            
            self.logger.info(f"Successfully added {len(new_user_ids)} users to property {request.property_id}")
            return PropertyResponse(message=message)

        except Exception as e:
            self.logger.error(f"Error adding users to property: {str(e)}")
            self.session.rollback()
            raise e
