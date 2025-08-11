from sqlalchemy import func
from services.inventory_service.app.dto.household import AddHouseholdItemDTO, HouseholdItemResponseDTO
from services.inventory_service.app.models.household import Household


class AddItem:

    def __init__(self, logger, session):
        self.logger = logger
        self.session = session

    def add_household_item(self, request: AddHouseholdItemDTO) -> HouseholdItemResponseDTO:
        self.logger.info(f"Adding household item with request: {request}")
        try:
            household_item  = Household(
                product_name=request.product_name,
                general_name=request.general_name,
                quantity=request.quantity,
                storage_id=request.storage_id,
                property_id=request.property_id,
                search_vector=func.to_tsvector('english', request.product_name + ' ' + request.general_name)
            )
            
            self.logger.info(f"Creating household item: {household_item}")

            self.session.add(household_item)
            self.session.commit()
            self.logger.info(f"Household item created successfully: {household_item}")
            return HouseholdItemResponseDTO(is_success=True)

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error adding household item: {e}")
            return HouseholdItemResponseDTO(is_success=False, error=str(e))
        
        finally:
            if self.session:
                self.session.close()
