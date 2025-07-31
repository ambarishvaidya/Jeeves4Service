from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.update_property import UpdateProperty
from app.dto.property import UpdatePropertyRequest, PropertyResponse
from app.models.property import Property


class TestUpdateProperty:
    """Test class for UpdateProperty service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = UpdateProperty(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_update_property_name_success(self):
        """Test successful property name update"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name="Updated Property Name",
            address=None
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Old Property Name"
        mock_property.address = "Old Address"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "Updated Property Name" in result.message
        assert "name" in result.message
        assert mock_property.name == "Updated Property Name"
        
        # Verify database operations
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_any_call("Updating property with ID: 123")
    
    def test_update_property_address_success(self):
        """Test successful property address update"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=456,
            name=None,
            address="New Address Street"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 456
        mock_property.name = "Test Property"
        mock_property.address = "Old Address"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "Test Property" in result.message
        assert "address" in result.message
        assert mock_property.address == "New Address Street"
        
        self.mock_session.commit.assert_called_once()
    
    def test_update_property_both_fields_success(self):
        """Test successful update of both name and address"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=789,
            name="New Name",
            address="New Address"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 789
        mock_property.name = "Old Name"
        mock_property.address = "Old Address"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "New Name" in result.message
        assert "name, address" in result.message
        assert mock_property.name == "New Name"
        assert mock_property.address == "New Address"
        
        self.mock_session.commit.assert_called_once()
    
    def test_update_property_not_found(self):
        """Test update when property does not exist"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=999,
            name="New Name"
        )
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Property with ID 999 not found"):
            self.service.update_property(update_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_update_property_no_fields_provided(self):
        """Test update when no fields are provided"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name=None,
            address=None
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert result.message == "No fields provided for update"
        
        # Verify no commit was called
        self.mock_session.commit.assert_not_called()
    
    def test_update_property_database_error(self):
        """Test update when database commit fails"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name="New Name"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Old Name"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Database error"):
            self.service.update_property(update_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error updating property: Database error")
    
    def test_update_property_with_empty_string_name(self):
        """Test update with empty string name"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name="",
            address=None
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Old Name"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert mock_property.name == ""
        self.mock_session.commit.assert_called_once()
    
    def test_update_property_with_none_address(self):
        """Test update address to None"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name=None,
            address=None
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        mock_property.address = "Old Address"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert - should not update anything since address=None means no update
        assert result.message == "No fields provided for update"
        assert mock_property.address == "Old Address"  # Unchanged
        
        self.mock_session.commit.assert_not_called()
    
    def test_update_property_logging_flow(self):
        """Test that logging works correctly throughout the flow"""
        # Arrange
        update_request = UpdatePropertyRequest(
            property_id=123,
            name="Logging Test Property"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Old Name"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property
        
        # Act
        result = self.service.update_property(update_request)
        
        # Assert
        self.mock_logger.info.assert_any_call("Updating property with ID: 123")
        self.mock_logger.info.assert_any_call("Property 123 updated successfully. Fields updated: name")
        self.mock_logger.error.assert_not_called()
