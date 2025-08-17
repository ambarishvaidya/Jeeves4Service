from operator import and_
from turtle import st
import spacy
from sqlalchemy import func, or_, and_, select, desc
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from services.shared.request_context import RequestContext
from services.household_service.app.dto.household import HouseholdItemDTO, SearchHouseholdItemResponseDTO
from services.household_service.app.models.household import Household
from services.property_service.app.models.storage import LocationPath, LocationPath, Storage


class FindItem:

    nlp = spacy.load("en_core_web_sm")

    def __init__ (self, logger, session):
        self.logger = logger
        self.session = session
        self.logger.info("FindItem service initialized successfully")

    def lemmatize_text(self, text: str) -> str:
        """Lemmatize text using spaCy NLP processing"""
        try:
            self.logger.debug(f"Starting lemmatization for text: '{text}'")
            
            if not text or not text.strip():
                self.logger.warning("Empty or whitespace-only text provided for lemmatization")
                return ""
            
            doc = self.nlp(text)
            lemmatized_tokens = [
                token.lemma_.lower()
                for token in doc
                if token.is_alpha and not token.is_stop
            ]
            
            result = " & ".join(lemmatized_tokens)
            self.logger.debug(f"Lemmatization completed. Original: '{text}' -> Lemmatized: '{result}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during text lemmatization: {e}. Using original text as fallback.")
            # Fallback to simple processing
            return text.lower().strip()

    def find_household_item(self, search_term: str) -> SearchHouseholdItemResponseDTO:
        """Find household items based on search term with comprehensive logging and error handling"""
        self.logger.info(f"Starting household item search with term: '{search_term}'")
        
        token_payload = RequestContext.get_token()
        
        # Input validation
        if not search_term or not search_term.strip():
            self.logger.warning("Empty or invalid search term provided")
            return SearchHouseholdItemResponseDTO(items=[])
        
        search_term = search_term.strip()
        self.logger.debug(f"Cleaned search term: '{search_term}'")
        
        try:
            # Step 1: Text processing
            self.logger.debug("Step 1: Processing search term with NLP")
            lemmatized_item = self.lemmatize_text(search_term)
            self.logger.info(f"Lemmatized search term: '{lemmatized_item}'")

            # Step 2: Query construction
            self.logger.debug("Step 2: Constructing database query")
            
            # Get user's accessible property IDs from token
            accessible_property_ids = []
            if token_payload:
                accessible_property_ids = token_payload.get_property_ids()
                self.logger.debug(f"User has access to properties: {accessible_property_ids}")
            
            # If user has no accessible properties, return empty results
            if not accessible_property_ids:
                self.logger.warning("User has no accessible properties, returning empty results")
                return SearchHouseholdItemResponseDTO(items=[])
            
            query = (
                    select(
                        Household,
                        func.ts_rank(Household.search_vector, func.to_tsquery('english', lemmatized_item)).label('rank')
                    )
                    .where(
                        and_(
                            # Filter by user's accessible properties
                            Household.property_id.in_(accessible_property_ids),
                            # Search conditions
                            or_(
                                Household.search_vector.op('@@')(func.to_tsquery('english', lemmatized_item)),
                                Household.product_name.ilike(f'%{search_term}%'),
                                Household.general_name.ilike(f'%{search_term}%'),
                                # func.similarity(Household.product_name, search_term) > 0.3,
                                # func.similarity(Household.general_name, search_term) > 0.3                        
                            )
                        )
                    )
                    .order_by(desc("rank"))
                    .limit(10)
                )
            self.logger.debug("Database query constructed successfully")

            # Step 3: Execute query
            self.logger.debug("Step 3: Executing database query")
            result = self.session.execute(query).scalars().all()
            self.logger.info(f"Database query executed successfully. Found {len(result)} household items matching '{search_term}'")

            # Step 4: Process results
            self.logger.debug("Step 4: Processing query results")
            household_items = []
            
            for idx, household_obj in enumerate(result, 1):
                try:
                    self.logger.debug(f"Processing household item {idx}/{len(result)}: ID={getattr(household_obj, 'id', 'Unknown')}")
                    
                    # Get location information
                    self.logger.debug(f"Fetching location for storage_id={household_obj.storage_id}, property_id={household_obj.property_id}")
                    storage_item = self.session.query(LocationPath).filter(
                        LocationPath.storage_id == household_obj.storage_id,
                        LocationPath.property_id == household_obj.property_id
                    ).first()
                    
                    location = storage_item.location_path if storage_item else 'Unknown'
                    self.logger.debug(f"Location resolved: '{location}'")
                    
                    # Create DTO
                    household_item = HouseholdItemDTO(
                        product_name=household_obj.product_name,
                        general_name=household_obj.general_name,
                        quantity=household_obj.quantity,
                        storage_id=household_obj.storage_id,
                        property_id=household_obj.property_id,
                        location=location
                    )
                    
                    household_items.append(household_item)
                    self.logger.debug(f"Successfully converted household item to DTO: {household_item.general_name}")
                    
                except Exception as item_error:
                    self.logger.error(f"Error processing individual household item {idx}: {item_error}. Skipping this item.")
                    continue

            self.logger.info(f"Successfully processed {len(household_items)} out of {len(result)} items")
            self.logger.info(f"Returning search results with {len(household_items)} household items")
            return SearchHouseholdItemResponseDTO(items=household_items)

        except SQLAlchemyError as db_error:
            self.logger.error(f"Database error during household item search: {db_error}")
            self.logger.debug(f"Database error details: {type(db_error).__name__}: {str(db_error)}")
            try:
                self.session.rollback()
                self.logger.debug("Database session rolled back successfully")
            except Exception as rollback_error:
                self.logger.error(f"Error during session rollback: {rollback_error}")
            return SearchHouseholdItemResponseDTO(items=[])
            
        except ValueError as val_error:
            self.logger.error(f"Value error during household item search: {val_error}")
            return SearchHouseholdItemResponseDTO(items=[])
            
        except Exception as e:
            self.logger.error(f"Unexpected error during household item search: {e}")
            self.logger.debug(f"Unexpected error details: {type(e).__name__}: {str(e)}", exc_info=True)
            return SearchHouseholdItemResponseDTO(items=[])

        finally:
            try:
                if self.session:
                    self.session.close()
                    self.logger.debug("Database session closed successfully")
            except Exception as close_error:
                self.logger.error(f"Error closing database session: {close_error}")
        
