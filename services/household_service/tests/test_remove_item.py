"""
Test cases for household_service remove_item functionality.

This test suite follows the patterns established in user_service and property_service
tests, providing comprehensive coverage for the RemoveItem service including:
- Successful item removal scenarios
- Item not found scenarios
- Error handling for database exceptions
- Session management and cleanup
- Logging verification
"""

from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from services.household_service.app.services.remove_item import RemoveItem
from services.household_service.app.dto.household import DeleteHouseholdItemDTO, HouseholdItemResponseDTO
from services.household_service.app.models.household import Household


class TestRemoveItem:
    """Test class for RemoveItem service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = RemoveItem(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_remove_item_success(self):
        """Test successful household item removal"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=123)
        
        # Mock household item from database
        mock_household = Mock(spec=Household)
        mock_household.id = 123
        mock_household.product_name = "Test Product"
        mock_household.general_name = "Test Item"
        mock_household.quantity = 2
        mock_household.storage_id = 101
        mock_household.property_id = 201
        
        # Mock successful database operations
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is True
        assert "Test Item" in result.msg
        assert "removed successfully" in result.msg
        assert result.err is None
        
        # Verify database operations were called
        self.mock_session.query.assert_called_once_with(Household)
        self.mock_session.query.return_value.filter_by.assert_called_once_with(id=123)
        self.mock_session.delete.assert_called_once_with(mock_household)
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify logging
        self.mock_logger.info.assert_called()
        self.mock_logger.debug.assert_called()
        self.mock_logger.error.assert_not_called()
    
    def test_remove_item_not_found(self):
        """Test removal when item does not exist"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=999)
        
        # Mock item not found
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "999" in result.msg
        assert "not found" in result.msg
        assert result.err == "Item does not exist"
        
        # Verify database operations
        self.mock_session.query.assert_called_once_with(Household)
        self.mock_session.query.return_value.filter_by.assert_called_once_with(id=999)
        self.mock_session.delete.assert_not_called()
        self.mock_session.commit.assert_not_called()
        self.mock_session.close.assert_called_once()
        
        # Verify logging
        self.mock_logger.warning.assert_called()
        assert any("not found in database" in str(call) for call in self.mock_logger.warning.call_args_list)
    
    def test_remove_item_integrity_error(self):
        """Test handling of database integrity constraint violations"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=456)
        
        # Mock household item
        mock_household = Mock(spec=Household)
        mock_household.id = 456
        mock_household.product_name = "Constrained Item"
        mock_household.general_name = "Test Item"
        mock_household.quantity = 1
        mock_household.storage_id = 102
        mock_household.property_id = 202
        
        # Mock database operations
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock(side_effect=IntegrityError("", "", "Foreign key constraint"))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "database constraints" in result.msg
        assert "Integrity constraint violation" in result.err
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify error logging
        self.mock_logger.error.assert_called()
        assert any("integrity constraint violation" in str(call).lower() for call in self.mock_logger.error.call_args_list)
    
    def test_remove_item_sqlalchemy_error(self):
        """Test handling of SQLAlchemy database errors"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=789)
        
        # Mock household item
        mock_household = Mock(spec=Household)
        mock_household.id = 789
        mock_household.general_name = "Error Item"
        
        # Mock database operations
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock(side_effect=SQLAlchemyError("Database connection failed"))
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "Database error occurred" in result.msg
        assert "SQLAlchemy error" in result.err
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify error logging
        self.mock_logger.error.assert_called()
    
    def test_remove_item_unexpected_error(self):
        """Test handling of unexpected errors"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=321)
        
        # Mock unexpected error during query
        self.mock_session.query.side_effect = ValueError("Unexpected error")
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        assert "unexpected error occurred" in result.msg
        assert "Unexpected error" in result.err
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify error logging
        self.mock_logger.error.assert_called()
    
    def test_remove_item_rollback_error(self):
        """Test handling when rollback itself fails"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=654)
        
        # Mock household item
        mock_household = Mock(spec=Household)
        mock_household.id = 654
        mock_household.general_name = "Rollback Error Item"
        
        # Mock database operations with rollback error
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock(side_effect=SQLAlchemyError("Commit failed"))
        self.mock_session.rollback = Mock(side_effect=Exception("Rollback failed"))
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert isinstance(result, HouseholdItemResponseDTO)
        assert result.is_success is False
        
        # Verify both errors are logged
        self.mock_logger.error.assert_called()
        error_calls = [str(call) for call in self.mock_logger.error.call_args_list]
        assert any("SQLAlchemy error" in call for call in error_calls)
        assert any("Error during rollback" in call for call in error_calls)
    
    def test_remove_item_session_cleanup_on_success(self):
        """Test that session is properly closed on successful operation"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=111)
        
        # Mock successful operations
        mock_household = Mock(spec=Household)
        mock_household.id = 111
        mock_household.general_name = "Success Item"
        
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify session cleanup in finally block
        self.mock_session.close.assert_called_once()
    
    def test_remove_item_session_cleanup_on_error(self):
        """Test that session is properly closed even when errors occur"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=222)
        
        # Mock error during operation
        self.mock_session.query.side_effect = Exception("Test error")
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is False
        
        # Verify session cleanup in finally block even after error
        self.mock_session.close.assert_called_once()
    
    def test_remove_item_session_close_error(self):
        """Test handling when session close itself fails"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=333)
        
        # Mock successful operation but close error
        mock_household = Mock(spec=Household)
        mock_household.id = 333
        mock_household.general_name = "Close Error Item"
        
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock(side_effect=Exception("Close failed"))
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is True  # Main operation should still succeed
        
        # Verify close error is logged
        self.mock_logger.error.assert_called()
        error_calls = [str(call) for call in self.mock_logger.error.call_args_list]
        assert any("Error closing database session" in call for call in error_calls)
    
    def test_remove_item_logging_flow(self):
        """Test that proper logging occurs throughout the process"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=444)
        
        # Mock successful operations
        mock_household = Mock(spec=Household)
        mock_household.id = 444
        mock_household.product_name = "Log Test Product"
        mock_household.general_name = "Log Test Item"
        mock_household.quantity = 3
        mock_household.storage_id = 103
        mock_household.property_id = 203
        
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify comprehensive logging
        info_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        debug_calls = [str(call) for call in self.mock_logger.debug.call_args_list]
        
        # Check key log messages
        assert any("Starting removal process" in call for call in info_calls)
        assert any("Found household item to delete" in call for call in info_calls)
        assert any("removed successfully from database" in call for call in info_calls)
        
        # Check debug messages
        assert any("Step 1: Querying database" in call for call in debug_calls)
        assert any("Step 2: Marking household item" in call for call in debug_calls)
        assert any("Step 3: Committing deletion" in call for call in debug_calls)
        assert any("Database session closed successfully" in call for call in debug_calls)
        
        # Verify no error logging
        self.mock_logger.error.assert_not_called()
    
    def test_remove_item_detailed_logging_content(self):
        """Test that item details are properly logged before deletion"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=555)
        
        # Mock household item with specific details
        mock_household = Mock(spec=Household)
        mock_household.id = 555
        mock_household.product_name = "Detailed Product"
        mock_household.general_name = "Detailed Item"
        mock_household.quantity = 5
        mock_household.storage_id = 104
        mock_household.property_id = 204
        
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is True
        
        # Verify detailed item logging
        info_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        detailed_log_found = False
        
        for call in info_calls:
            if "Found household item to delete" in call:
                assert "ID=555" in call
                assert "product_name='Detailed Product'" in call
                assert "general_name='Detailed Item'" in call
                assert "quantity=5" in call
                assert "storage_id=104" in call
                assert "property_id=204" in call
                detailed_log_found = True
                break
        
        assert detailed_log_found, "Detailed item logging not found"
    
    def test_remove_item_with_none_product_name(self):
        """Test removal of item with None product_name"""
        # Arrange
        delete_request = DeleteHouseholdItemDTO(id=666)
        
        # Mock household item with None product_name
        mock_household = Mock(spec=Household)
        mock_household.id = 666
        mock_household.product_name = None
        mock_household.general_name = "Generic Item"
        mock_household.quantity = 1
        mock_household.storage_id = 105
        mock_household.property_id = 205
        
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_household
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.close = Mock()
        
        # Act
        result = self.service.remove_item(delete_request)
        
        # Assert
        assert result.is_success is True
        assert "Generic Item" in result.msg
        
        # Verify logging handles None product_name gracefully
        info_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        detailed_log_found = any("product_name='None'" in call or "product_name=None" in call 
                                for call in info_calls)
        assert detailed_log_found
    
    def test_remove_item_initialization_logging(self):
        """Test that service initialization is properly logged"""
        # The service is already initialized in setup_method
        # Verify initialization logging
        self.mock_logger.info.assert_called()
        init_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        assert any("RemoveItem service initialized successfully" in call for call in init_calls)
