from sqlalchemy.exc import SQLAlchemyError, DatabaseError, IntegrityError
from services.household_service.app.dto.household import DeleteHouseholdItemDTO, HouseholdItemResponseDTO
from services.household_service.app.models.household import Household


class RemoveItem:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session
        self.logger.info("RemoveItem service initialized successfully")

    def remove_item(self, item_to_delete: DeleteHouseholdItemDTO) -> HouseholdItemResponseDTO:
        """Remove a household item with comprehensive logging and error handling"""
        
        item_id = item_to_delete.id
        self.logger.info(f"Starting removal process for household item with ID: {item_id}")
        
        try:
            # Step 1: Query for the item
            self.logger.debug(f"Step 1: Querying database for household item with ID: {item_id}")
            item = self.session.query(Household).filter_by(id=item_id).first()
            
            if not item:
                self.logger.warning(f"Household item with ID {item_id} not found in database")
                return HouseholdItemResponseDTO(
                    msg=f"Item with ID {item_id} not found",
                    err="Item does not exist",
                    is_success=False
                )
            
            # Log item details before deletion
            self.logger.info(f"Found household item to delete: ID={item.id}, "
                           f"product_name='{item.product_name}', "
                           f"general_name='{item.general_name}', "
                           f"quantity={item.quantity}, "
                           f"storage_id={item.storage_id}, "
                           f"property_id={item.property_id}")
            
            # Step 2: Delete the item
            self.logger.debug(f"Step 2: Marking household item {item_id} for deletion")
            self.session.delete(item)
            
            # Step 3: Commit the transaction
            self.logger.debug(f"Step 3: Committing deletion of household item {item_id}")
            self.session.commit()
            
            self.logger.info(f"Household item with ID {item_id} removed successfully from database")
            return HouseholdItemResponseDTO(
                msg=f"Item '{item.general_name}' removed successfully",
                is_success=True
            )
            
        except IntegrityError as integrity_error:
            self.logger.error(f"Database integrity constraint violation while removing item {item_id}: {integrity_error}")
            try:
                self.session.rollback()
                self.logger.debug(f"Database transaction rolled back successfully for item {item_id}")
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback for item {item_id}: {rollback_error}")
            
            return HouseholdItemResponseDTO(
                msg="Cannot remove item due to database constraints",
                err=f"Integrity constraint violation: {str(integrity_error)}",
                is_success=False
            )
            
        except SQLAlchemyError as sqlalchemy_error:
            self.logger.error(f"SQLAlchemy error while removing household item {item_id}: {sqlalchemy_error}")
            try:
                self.session.rollback()
                self.logger.debug(f"Database transaction rolled back successfully for item {item_id}")
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback for item {item_id}: {rollback_error}")
            
            return HouseholdItemResponseDTO(
                msg="Database error occurred while removing item",
                err=f"SQLAlchemy error: {str(sqlalchemy_error)}",
                is_success=False
            )
            
        except Exception as unexpected_error:
            self.logger.error(f"Unexpected error while removing household item {item_id}: {unexpected_error}")
            self.logger.debug(f"Unexpected error details: {type(unexpected_error).__name__}: {str(unexpected_error)}", 
                            exc_info=True)
            try:
                self.session.rollback()
                self.logger.debug(f"Database transaction rolled back successfully for item {item_id}")
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback for item {item_id}: {rollback_error}")
            
            return HouseholdItemResponseDTO(
                msg="An unexpected error occurred while removing item",
                err=f"Unexpected error: {str(unexpected_error)}",
                is_success=False
            )
            
        finally:
            # Ensure session is always closed
            try:
                if self.session:
                    self.session.close()
                    self.logger.debug(f"Database session closed successfully after processing item {item_id}")
            except Exception as close_error:
                self.logger.error(f"Error closing database session for item {item_id}: {close_error}")