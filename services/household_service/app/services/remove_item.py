from services.household_service.app.dto.household import DeleteHouseholdItemDTO, HouseholdItemResponseDTO
from services.household_service.app.models.household import Household


class RemoveItem:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session

    def remove_item(self, item_to_delete: DeleteHouseholdItemDTO):
        self.logger.info(f"Removing item with id: {item_to_delete}")
        try:
            item = self.session.query(Household).filter_by(id=item_to_delete.id).first()
            if not item:
                self.logger.warning(f"Item with id {item_to_delete.id} not found")
                return {"success": False, "message": "Item not found"}
            self.session.delete(item)
            self.session.commit()
            self.logger.info(f"Item with id {item_to_delete.id} removed successfully")
            return HouseholdItemResponseDTO(
                msg="Item removed successfully",
                is_success=True
            )
        except Exception as e:
            self.logger.error(f"Error removing item with id {item_to_delete.id}: {e}")
            self.session.rollback()
            return HouseholdItemResponseDTO(
                msg="Error removing item",
                is_success=False
            )
        finally:
            if self.session:
                self.session.close()