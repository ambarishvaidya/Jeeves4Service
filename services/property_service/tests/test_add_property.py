from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.property_service.app.services.add_property import AddProperty
from services.property_service.app.dto.property import NewPropertyRequest, PropertyResponse
from services.property_service.app.models.property import Property, PropertyAssociation


class TestAddProperty:
    """Test class for AddProperty service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = AddProperty(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_add_property_success(self):
        """Test successful property addition"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Test Property",
            address="123 Test Street",
            created_by=1
        )
        
        # Mock property with ID after flush
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Configure session to simulate successful database operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        self.mock_session.commit = Mock()
        
        # Mock the property creation to return the mock_property with ID
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            
            # Act
            result = self.service.add_property(new_property_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert result.message == "Property 'Test Property' added successfully with ID 123"
        
        # Verify Property was created with correct parameters
        mock_property_class.assert_called_once_with(
            name="Test Property",
            address="123 Test Street",
            created_by=1
        )
        
        # Verify database operations were called in correct order
        assert self.mock_session.add.call_count == 2  # Property and PropertyAssociation
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify logging
        self.mock_logger.info.assert_called_once_with("Adding new property")
    
    def test_add_property_with_property_association(self):
        """Test that property association is created correctly"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Associated Property",
            address="456 Association Ave",
            created_by=42
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 456
        mock_property.name = "Associated Property"
        
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        self.mock_session.commit = Mock()
        
        # Act
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class, \
             patch('services.property_service.app.services.add_property.PropertyAssociation') as mock_association_class:
            
            mock_property_class.return_value = mock_property
            mock_association = Mock(spec=PropertyAssociation)
            mock_association_class.return_value = mock_association
            
            result = self.service.add_property(new_property_request)
        
        # Assert
        # Verify PropertyAssociation was created with correct parameters
        mock_association_class.assert_called_once_with(
            property_id=456,
            user_id=42
        )
        
        # Verify both objects were added to session
        expected_calls = [((mock_property,),), ((mock_association,),)]
        actual_calls = self.mock_session.add.call_args_list
        assert len(actual_calls) == 2
    
    def test_add_property_empty_name(self):
        """Test property addition with empty name"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="",
            address="123 Test Street",
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = ""
        
        # Act
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            result = self.service.add_property(new_property_request)
        
        # Assert - should still work but with empty name
        assert isinstance(result, PropertyResponse)
        assert result.message == "Property '' added successfully with ID 123"
    
    def test_add_property_none_address(self):
        """Test property addition with None address"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="No Address Property",
            address=None,
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 789
        mock_property.name = "No Address Property"
        
        # Act
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            result = self.service.add_property(new_property_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert result.message == "Property 'No Address Property' added successfully with ID 789"
        
        # Verify Property was created with None address
        mock_property_class.assert_called_once_with(
            name="No Address Property",
            address=None,
            created_by=1
        )
    
    def test_add_property_database_error_on_add(self):
        """Test property addition when database add fails"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Error Property",
            address="Error Street",
            created_by=1
        )
        
        # Configure session to raise exception on add
        self.mock_session.add.side_effect = SQLAlchemyError("Database connection failed")
        
        # Act & Assert
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = Mock(spec=Property)
            
            with pytest.raises(SQLAlchemyError, match="Database connection failed"):
                self.service.add_property(new_property_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        
        # Verify error was logged
        self.mock_logger.error.assert_called_once_with("Error adding property: Database connection failed")
    
    def test_add_property_database_error_on_flush(self):
        """Test property addition when database flush fails"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Flush Error Property",
            address="Flush Error Street",
            created_by=1
        )
        
        # Configure session to raise exception on flush
        self.mock_session.flush.side_effect = SQLAlchemyError("Flush operation failed")
        
        # Act & Assert
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = Mock(spec=Property)
            
            with pytest.raises(SQLAlchemyError, match="Flush operation failed"):
                self.service.add_property(new_property_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding property: Flush operation failed")
    
    def test_add_property_database_error_on_commit(self):
        """Test property addition when database commit fails"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Commit Error Property",
            address="Commit Error Street",
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 999
        
        # Configure session to raise exception on commit
        self.mock_session.commit.side_effect = SQLAlchemyError("Commit operation failed")
        
        # Act & Assert
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            
            with pytest.raises(SQLAlchemyError, match="Commit operation failed"):
                self.service.add_property(new_property_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding property: Commit operation failed")
    
    def test_add_property_association_creation_error(self):
        """Test property addition when PropertyAssociation creation fails"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Association Error Property",
            address="Association Error Street",
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 555
        
        # Act & Assert
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class, \
             patch('services.property_service.app.services.add_property.PropertyAssociation') as mock_association_class:
            
            mock_property_class.return_value = mock_property
            mock_association_class.side_effect = Exception("Association creation failed")
            
            with pytest.raises(Exception, match="Association creation failed"):
                self.service.add_property(new_property_request)
        
        # Verify rollback and error logging
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding property: Association creation failed")
    
    def test_add_property_transaction_rollback_on_any_exception(self):
        """Test that transaction is rolled back on any exception"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Rollback Test Property",
            address="Rollback Street",
            created_by=1
        )
        
        # Configure session to raise a generic exception
        self.mock_session.add.side_effect = Exception("Generic error")
        
        # Act & Assert
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = Mock(spec=Property)
            
            with pytest.raises(Exception, match="Generic error"):
                self.service.add_property(new_property_request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        
        # Verify commit was not called
        self.mock_session.commit.assert_not_called()
    
    def test_add_property_logging_flow(self):
        """Test that logging works correctly throughout the flow"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Logging Test Property",
            address="Logging Street",
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 777
        mock_property.name = "Logging Test Property"
        
        # Act
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            result = self.service.add_property(new_property_request)
        
        # Assert
        # Verify info logging was called at the start
        self.mock_logger.info.assert_called_once_with("Adding new property")
        
        # Verify no error logging occurred (since this was successful)
        self.mock_logger.error.assert_not_called()
    
    def test_add_property_with_special_characters(self):
        """Test property addition with special characters in name and address"""
        # Arrange
        new_property_request = NewPropertyRequest(
            name="Property with Special Chars !@#$%^&*()",
            address="123 O'Reilly Street, Apt #5",
            created_by=1
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 888
        mock_property.name = "Property with Special Chars !@#$%^&*()"
        
        # Act
        with patch('services.property_service.app.services.add_property.Property') as mock_property_class:
            mock_property_class.return_value = mock_property
            result = self.service.add_property(new_property_request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "Property with Special Chars !@#$%^&*()" in result.message
        assert "888" in result.message

    