from turtle import st
import spacy
from sqlalchemy import func, or_, select, desc
from services.household_service.app.dto.household import HouseholdItemDTO, SearchHouseholdItemResponseDTO
from services.household_service.app.models.household import Household
from services.property_service.app.models.storage import LocationPath, LocationPath, Storage


class FindItem:

    nlp = spacy.load("en_core_web_sm")

    def __init__ (self, logger, session):
        self.logger = logger
        self.session = session

    def lemmatize_text(self, text: str) -> str:
        doc = self.nlp(text)
        return " & ".join([
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop
        ])


    def find_household_item(self, item: str) -> SearchHouseholdItemResponseDTO:
        self.logger.info(f"Finding household item with search term: {item}")
        try:
            lemmatized_item = self.lemmatize_text(item)
            self.logger.info(f"Lemmatized search term: {lemmatized_item}")

            query = (
                    select(
                        Household,
                        func.ts_rank(Household.search_vector, func.to_tsquery('english', lemmatized_item)).label('rank')
                    )
                    .where(
                        or_(
                            Household.search_vector.op('@@')(func.to_tsquery('english', lemmatized_item)),
                            Household.product_name.ilike(f'%{item}%'),
                            Household.general_name.ilike(f'%{item}%'),
                            # func.similarity(Household.product_name, item) > 0.3,
                            # func.similarity(Household.general_name, item) > 0.3
                        )
                    )
                    .order_by(desc("rank"))
                    .limit(10)
                )

            result = self.session.execute(query).scalars().all()
            self.logger.info(f"Found {len(result)} household items matching '{item}'")
            household_items = list()
            for item in result:
                self.logger.info(f"Found household item: {item}")
                storage_item = self.session.query(LocationPath).filter(LocationPath.storage_id == item.storage_id 
                                                                       and LocationPath.property_id == item.property_id).first()
                household_item = HouseholdItemDTO(
                    product_name=item.product_name,
                    general_name=item.general_name,
                    quantity=item.quantity,
                    storage_id=item.storage_id,
                    property_id=item.property_id,
                    location=storage_item.location_path if storage_item else 'Unknown'
                )
                self.logger.info(f"Converted household item to DTO: {household_item}")
                household_items.append(household_item)

            self.logger.info(f"Returning {len(household_items)} household items")
            return SearchHouseholdItemResponseDTO(items=household_items)

        except Exception as e:
            self.logger.error(f"Error finding household item: {e}")
            return SearchHouseholdItemResponseDTO(items=[])

        finally:
            if self.session:
                self.session.close()
        
