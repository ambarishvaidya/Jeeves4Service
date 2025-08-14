"""
Test cases for household_service find_item functionality.

This test suite provides comprehensive coverage for the FindItem service including:
- Successful item search scenarios
- Text lemmatization and NLP processing
- Database query execution and result processing
- Location resolution from storage paths
- Error handling for various failure scenarios
- Session management and cleanup
- Input validation and edge cases
"""

from unittest.mock import Mock, patch, MagicMock
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, DatabaseError

from services.household_service.app.services.find_item import FindItem
from services.household_service.app.dto.household import HouseholdItemDTO, SearchHouseholdItemResponseDTO
from services.household_service.app.models.household import Household
from services.property_service.app.models.storage import LocationPath


class TestFindItem:
    """Test class for FindItem service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Mock spaCy NLP model to avoid loading actual model in tests
        with patch('services.household_service.app.services.find_item.spacy.load') as mock_spacy:
            mock_nlp = Mock()
            mock_spacy.return_value = mock_nlp
            
            # Create service instance with mocked dependencies
            self.service = FindItem(
                logger=self.mock_logger,
                session=self.mock_session
            )
            self.service.nlp = mock_nlp
    
    def test_lemmatize_text_success(self):
        """Test successful text lemmatization"""
        # Arrange
        mock_token1 = Mock()
        mock_token1.lemma_ = "clean"
        mock_token1.is_alpha = True
        mock_token1.is_stop = False
        
        mock_token2 = Mock()
        mock_token2.lemma_ = "product"
        mock_token2.is_alpha = True
        mock_token2.is_stop = False
        
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2]))
        self.service.nlp.return_value = mock_doc
        
        # Act
        result = self.service.lemmatize_text("cleaning products")
        
        # Assert
        assert result == "clean & product"
        self.service.nlp.assert_called_once_with("cleaning products")
        self.mock_logger.debug.assert_called()
    
    def test_lemmatize_text_with_stop_words(self):
        """Test lemmatization filtering out stop words and non-alpha tokens"""
        # Arrange
        mock_token1 = Mock()
        mock_token1.lemma_ = "clean"
        mock_token1.is_alpha = True
        mock_token1.is_stop = False
        
        mock_token2 = Mock()  # Stop word
        mock_token2.lemma_ = "the"
        mock_token2.is_alpha = True
        mock_token2.is_stop = True
        
        mock_token3 = Mock()  # Non-alpha
        mock_token3.lemma_ = "123"
        mock_token3.is_alpha = False
        mock_token3.is_stop = False
        
        mock_token4 = Mock()
        mock_token4.lemma_ = "product"
        mock_token4.is_alpha = True
        mock_token4.is_stop = False
        
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2, mock_token3, mock_token4]))
        self.service.nlp.return_value = mock_doc
        
        # Act
        result = self.service.lemmatize_text("clean the 123 products")
        
        # Assert
        assert result == "clean & product"
    
    def test_lemmatize_text_empty_input(self):
        """Test lemmatization with empty input"""
        # Act
        result = self.service.lemmatize_text("")
        
        # Assert
        assert result == ""
        self.mock_logger.warning.assert_called_with("Empty or whitespace-only text provided for lemmatization")
    
    def test_lemmatize_text_nlp_error_fallback(self):
        """Test lemmatization fallback when NLP processing fails"""
        # Arrange
        self.service.nlp.side_effect = Exception("NLP processing failed")
        
        # Act
        result = self.service.lemmatize_text("Test Product")
        
        # Assert
        assert result == "test product"
        self.mock_logger.error.assert_called()
    
    def test_find_household_item_success(self):
        """Test successful household item search"""
        # Arrange
        search_term = "cleaning spray"
        
        # Mock lemmatization
        with patch.object(self.service, 'lemmatize_text', return_value="clean & spray"):
            # Mock database query results
            mock_household1 = Mock(spec=Household)
            mock_household1.id = 1
            mock_household1.product_name = "Lysol"
            mock_household1.general_name = "Cleaning Spray"
            mock_household1.quantity = 2
            mock_household1.storage_id = 101
            mock_household1.property_id = 201
            
            mock_household2 = Mock(spec=Household)
            mock_household2.id = 2
            mock_household2.product_name = None
            mock_household2.general_name = "Generic Spray"
            mock_household2.quantity = 1
            mock_household2.storage_id = 102
            mock_household2.property_id = 201
            
            # Mock database execution
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = [mock_household1, mock_household2]
            self.mock_session.execute.return_value = mock_execute_result
            
            # Mock location path queries
            mock_location1 = Mock(spec=LocationPath)
            mock_location1.location_path = "Kitchen > Under Sink"
            mock_location2 = Mock(spec=LocationPath)
            mock_location2.location_path = "Bathroom > Cabinet"
            
            self.mock_session.query.return_value.filter.return_value.first.side_effect = [
                mock_location1, mock_location2
            ]
            
            # Mock session close
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 2
        
        # Check first item
        item1 = result.items[0]
        assert item1.product_name == "Lysol"
        assert item1.general_name == "Cleaning Spray"
        assert item1.quantity == 2
        assert item1.storage_id == 101
        assert item1.property_id == 201
        assert item1.location == "Kitchen > Under Sink"
        
        # Check second item
        item2 = result.items[1]
        assert item2.product_name is None
        assert item2.general_name == "Generic Spray"
        assert item2.quantity == 1
        assert item2.storage_id == 102
        assert item2.property_id == 201
        assert item2.location == "Bathroom > Cabinet"
        
        # Verify database operations
        self.mock_session.execute.assert_called_once()
        assert self.mock_session.query.call_count == 2
        self.mock_session.close.assert_called_once()
        
        # Verify logging
        self.mock_logger.info.assert_called()
        assert any("Starting household item search" in str(call) for call in self.mock_logger.info.call_args_list)
    
    def test_find_household_item_no_results(self):
        """Test search with no matching results"""
        # Arrange
        search_term = "nonexistent item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="nonexistent & item"):
            # Mock empty results
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = []
            self.mock_session.execute.return_value = mock_execute_result
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        self.mock_session.close.assert_called_once()
    
    def test_find_household_item_location_not_found(self):
        """Test search when location path is not found"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock household item
            mock_household = Mock(spec=Household)
            mock_household.id = 1
            mock_household.product_name = "Test Product"
            mock_household.general_name = "Test Item"
            mock_household.quantity = 1
            mock_household.storage_id = 999
            mock_household.property_id = 999
            
            # Mock database execution
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = [mock_household]
            self.mock_session.execute.return_value = mock_execute_result
            
            # Mock location not found
            self.mock_session.query.return_value.filter.return_value.first.return_value = None
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert len(result.items) == 1
        assert result.items[0].location == "Unknown"
    
    def test_find_household_item_empty_search_term(self):
        """Test search with empty search term"""
        # Act
        result = self.service.find_household_item("")
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        self.mock_logger.warning.assert_called_with("Empty or invalid search term provided")
    
    def test_find_household_item_whitespace_search_term(self):
        """Test search with whitespace-only search term"""
        # Act
        result = self.service.find_household_item("   ")
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        self.mock_logger.warning.assert_called_with("Empty or invalid search term provided")
    
    def test_find_household_item_database_error(self):
        """Test handling of database errors"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock database error
            self.mock_session.execute.side_effect = SQLAlchemyError("Database connection failed")
            self.mock_session.rollback = Mock()
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        
        # Verify error handling
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
        self.mock_logger.error.assert_called()
        assert any("Database error" in str(call) for call in self.mock_logger.error.call_args_list)
    
    def test_find_household_item_individual_item_processing_error(self):
        """Test handling when individual item processing fails"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock household items - one good, one that will cause error
            mock_household1 = Mock(spec=Household)
            mock_household1.id = 1
            mock_household1.product_name = "Good Item"
            mock_household1.general_name = "Working Item"
            mock_household1.quantity = 1
            mock_household1.storage_id = 101
            mock_household1.property_id = 201
            
            mock_household2 = Mock(spec=Household)
            mock_household2.id = 2
            # This will cause AttributeError when accessing properties
            mock_household2.product_name = Mock(side_effect=AttributeError("Access failed"))
            
            # Mock database execution
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = [mock_household1, mock_household2]
            self.mock_session.execute.return_value = mock_execute_result
            
            # Mock location for the good item
            mock_location = Mock(spec=LocationPath)
            mock_location.location_path = "Test Location"
            self.mock_session.query.return_value.filter.return_value.first.return_value = mock_location
            
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 1  # Only the good item should be processed
        assert result.items[0].product_name == "Good Item"
        
        # Verify error logging for the failed item
        self.mock_logger.error.assert_called()
        assert any("Error processing individual household item" in str(call) for call in self.mock_logger.error.call_args_list)
    
    def test_find_household_item_value_error(self):
        """Test handling of value errors"""
        # Arrange
        search_term = "test item"
        
        # Mock lemmatize_text to succeed, but make the actual processing fail with ValueError
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock session.execute to raise ValueError
            self.mock_session.execute.side_effect = ValueError("Invalid value")
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        self.mock_logger.error.assert_called()
        assert any("Value error" in str(call) for call in self.mock_logger.error.call_args_list)
    
    def test_find_household_item_unexpected_error(self):
        """Test handling of unexpected errors"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', side_effect=RuntimeError("Unexpected error")):
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        assert len(result.items) == 0
        self.mock_logger.error.assert_called()
        assert any("Unexpected error" in str(call) for call in self.mock_logger.error.call_args_list)
    
    def test_find_household_item_session_cleanup_on_success(self):
        """Test that session is properly closed on successful operation"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock empty results for simplicity
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = []
            self.mock_session.execute.return_value = mock_execute_result
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert result.items == []
        self.mock_session.close.assert_called_once()
    
    def test_find_household_item_session_cleanup_on_error(self):
        """Test that session is properly closed even when errors occur"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock database error
            self.mock_session.execute.side_effect = Exception("Test error")
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert len(result.items) == 0
        self.mock_session.close.assert_called_once()
    
    def test_find_household_item_session_close_error(self):
        """Test handling when session close itself fails"""
        # Arrange
        search_term = "test item"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & item"):
            # Mock empty results
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = []
            self.mock_session.execute.return_value = mock_execute_result
            
            # Mock session close error
            self.mock_session.close = Mock(side_effect=Exception("Close failed"))
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        self.mock_logger.error.assert_called()
        assert any("Error closing database session" in str(call) for call in self.mock_logger.error.call_args_list)
    
    def test_find_household_item_logging_flow(self):
        """Test that proper logging occurs throughout the process"""
        # Arrange
        search_term = "test cleaning product"
        
        with patch.object(self.service, 'lemmatize_text', return_value="test & clean & product"):
            # Mock empty results for simplicity
            mock_execute_result = Mock()
            mock_execute_result.scalars.return_value.all.return_value = []
            self.mock_session.execute.return_value = mock_execute_result
            self.mock_session.close = Mock()
        
        # Act
        result = self.service.find_household_item(search_term)
        
        # Assert
        assert isinstance(result, SearchHouseholdItemResponseDTO)
        
        # Verify comprehensive logging
        info_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        debug_calls = [str(call) for call in self.mock_logger.debug.call_args_list]
        
        # Check key log messages
        assert any("Starting household item search" in call for call in info_calls)
        assert any("Lemmatized search term" in call for call in info_calls)
        assert any("Database query executed successfully" in call for call in info_calls)
        assert any("Returning search results" in call for call in info_calls)
        
        # Check debug messages
        assert any("Step 1: Processing search term" in call for call in debug_calls)
        assert any("Step 2: Constructing database query" in call for call in debug_calls)
        assert any("Step 3: Executing database query" in call for call in debug_calls)
        assert any("Step 4: Processing query results" in call for call in debug_calls)

    def test_find_household_item_search_term_trimming(self):
        """Test that search terms are properly trimmed"""
        # Arrange
        search_term = "  test item  "
        
        # Mock empty results
        mock_execute_result = Mock()
        mock_execute_result.scalars.return_value.all.return_value = []
        self.mock_session.execute.return_value = mock_execute_result
        self.mock_session.close = Mock()
        
        # We need to let the actual lemmatize_text method run to verify the trimmed input
        with patch.object(self.service, 'lemmatize_text', wraps=self.service.lemmatize_text) as mock_lemmatize:
            # Mock the NLP processing within lemmatize_text
            mock_doc = Mock()
            mock_doc.__iter__ = Mock(return_value=iter([]))  # Empty tokens for simplicity
            self.service.nlp.return_value = mock_doc
        
            # Act
            result = self.service.find_household_item(search_term)
        
            # Assert
            assert isinstance(result, SearchHouseholdItemResponseDTO)
            
            # Verify that trimmed search term was used in lemmatize_text
            mock_lemmatize.assert_called_with("test item")
            
        # Verify debug logging shows the trimmed term
        debug_calls = [str(call) for call in self.mock_logger.debug.call_args_list]
        assert any("Cleaned search term: 'test item'" in call for call in debug_calls)
