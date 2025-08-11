"""
Test cases for household_service add_item functionality.

This test suite follows the patterns established in user_service and property_service
tests, providing comprehensive coverage for the AddItem service including:
- Successful item addition scenarios
- Error handling for database exceptions
- Session management and cleanup
- Search vector creation with various input combinations
- Logging verification
"""

from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from services.household_service.app.services.add_item import AddItem
from services.household_service.app.dto.household import AddHouseholdItemDTO, HouseholdItemResponseDTO
from services.household_service.app.models.household import Household


class TestAddItem:
    """Test class for AddItem service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = AddItem(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_add_household_item_success(self):
        """Test successful household item addition"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Fairy Liquid",
            general_name="Dishwashing Soap",
            quantity=2,
            storage_id=101,
            property_id=201
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is True
        assert result.err is None
        
        # Verify database operations were called
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify the item was created with correct parameters
        added_item = self.mock_session.add.call_args[0][0]
        assert isinstance(added_item, Household)
        assert added_item.product_name == "Fairy Liquid"
        assert added_item.general_name == "Dishwashing Soap"
        assert added_item.quantity == 2
        assert added_item.storage_id == 101
        assert added_item.property_id == 201
        
        # Verify logging
        self.mock_logger.info.assert_called()
        self.mock_logger.error.assert_not_called()
    
    def test_add_household_item_success_without_product_name(self):
        """Test successful household item addition without product name"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            general_name="Generic Cleaning Spray",
            quantity=1,
            storage_id=102,
            property_id=202
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is True
        assert result.err is None
        
        # Verify the item was created with correct parameters
        added_item = self.mock_session.add.call_args[0][0]
        assert isinstance(added_item, Household)
        assert added_item.product_name is None
        assert added_item.general_name == "Generic Cleaning Spray"
        assert added_item.quantity == 1
        assert added_item.storage_id == 102
        assert added_item.property_id == 202
        
        # Verify database operations were called
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()
    
    def test_add_household_item_with_default_quantity(self):
        """Test household item addition with default quantity"""
        # Arrange - quantity defaults to 1 in DTO
        add_item_request = AddHouseholdItemDTO(
            product_name="Duracell AA",
            general_name="Batteries",
            storage_id=103,
            property_id=203
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is True
        
        # Verify the item was created with default quantity
        added_item = self.mock_session.add.call_args[0][0]
        assert added_item.quantity == 1
    
    def test_add_household_item_database_error(self):
        """Test handling of database errors during item addition"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Test Product",
            general_name="Test Item",
            quantity=3,
            storage_id=104,
            property_id=204
        )
        
        # Mock database error
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock(side_effect=SQLAlchemyError("Database connection failed"))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "Database connection failed" in result.err
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify error logging
        self.mock_logger.error.assert_called_once()
    
    def test_add_household_item_integrity_error(self):
        """Test handling of integrity constraint violations"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Duplicate Item",
            general_name="Test Item",
            quantity=1,
            storage_id=105,
            property_id=205
        )
        
        # Mock integrity error
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock(side_effect=IntegrityError("", "", ""))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert result.err is not None
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
    
    def test_add_household_item_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Test Product",
            general_name="Test Item",
            quantity=1,
            storage_id=106,
            property_id=206
        )
        
        # Mock unexpected exception during session.add
        self.mock_session.add = Mock(side_effect=ValueError("Unexpected error"))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "Unexpected error" in result.err
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
    
    def test_add_household_item_search_vector_creation(self):
        """Test that search vector is properly created with product and general name"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Tide Pods",
            general_name="Laundry Detergent",
            quantity=1,
            storage_id=107,
            property_id=207
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify the search vector is set (func.to_tsvector is used)
        added_item = self.mock_session.add.call_args[0][0]
        assert added_item.search_vector is not None
    
    def test_add_household_item_search_vector_with_none_product_name(self):
        """Test search vector creation when product_name is None"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            general_name="Generic Tool",
            quantity=1,
            storage_id=108,
            property_id=208
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify the item was created even with None product_name
        added_item = self.mock_session.add.call_args[0][0]
        assert added_item.product_name is None
        assert added_item.general_name == "Generic Tool"
        assert added_item.search_vector is not None
    
    def test_add_household_item_logging_flow(self):
        """Test that proper logging occurs throughout the process"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            product_name="Test Product",
            general_name="Test Item",
            quantity=5,
            storage_id=109,
            property_id=209
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify logging calls
        assert self.mock_logger.info.call_count >= 3  # At least 3 info logs expected
        self.mock_logger.error.assert_not_called()
        
        # Check specific log messages
        log_messages = [call.args[0] for call in self.mock_logger.info.call_args_list]
        assert any("Adding household item with request:" in msg for msg in log_messages)
        assert any("Creating household item:" in msg for msg in log_messages)
        assert any("Household item created successfully:" in msg for msg in log_messages)

    def test_add_household_item_session_cleanup_on_success(self):
        """Test that session is properly closed on successful operation"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            general_name="Cleanup Test Item",
            storage_id=110,
            property_id=210
        )
        
        # Mock successful database operations
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify session cleanup in finally block
        self.mock_session.close.assert_called_once()
    
    def test_add_household_item_session_cleanup_on_error(self):
        """Test that session is properly closed even when errors occur"""
        # Arrange
        add_item_request = AddHouseholdItemDTO(
            general_name="Error Test Item",
            storage_id=111,
            property_id=211
        )
        
        # Mock database error
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock(side_effect=Exception("Test error"))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.add_household_item(add_item_request)
        
        # Assert
        assert result.is_success is False
        
        # Verify session cleanup in finally block even after error
        self.mock_session.close.assert_called_once()
