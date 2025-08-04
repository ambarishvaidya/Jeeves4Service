from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.property_service.app.services.add_users_property import AddUsersProperty
from services.property_service.app.dto.property import AddUsersPropertyRequest, PropertyResponse
from services.property_service.app.models.property import Property, PropertyAssociation


class TestAddUsersProperty:
    """Test class for AddUsersProperty service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = AddUsersProperty(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_add_users_to_property_success(self):
        """Test successful addition of users to property"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[1, 2, 3]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Setup query chain for property lookup
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        # Setup query chain for association lookup (no existing associations)
        association_query = Mock()
        association_query.filter.return_value.all.return_value = []
        
        # Configure session.query to return different mocks based on the model
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
            
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_users_to_property(request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "Added 3 users to property 'Test Property'" in result.message
        
        # Verify database operations - 3 associations should be added
        assert self.mock_session.add.call_count == 3
        self.mock_session.commit.assert_called_once()
    
    def test_add_users_property_not_found(self):
        """Test when property does not exist"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=999,
            user_ids=[1, 2]
        )
        
        # Setup query chain for property lookup (property not found)
        property_query = Mock()
        property_query.filter.return_value.first.return_value = None
        
        # Configure session.query to return the property query mock
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                # This shouldn't be called since property doesn't exist
                return Mock()
            return Mock()  # fallback for any unexpected models
            
        self.mock_session.query.side_effect = query_side_effect
        
        # Act & Assert
        with pytest.raises(ValueError, match="Property with ID 999 not found"):
            self.service.add_users_to_property(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_add_users_some_already_associated(self):
        """Test when some users are already associated with property"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[1, 2, 3, 4]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Mock existing associations for users 1 and 3
        existing_association_1 = Mock(spec=PropertyAssociation)
        existing_association_1.user_id = 1
        existing_association_3 = Mock(spec=PropertyAssociation)
        existing_association_3.user_id = 3
        
        # Setup query chain for property lookup
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        # Setup query chain for association lookup
        association_query = Mock()
        association_query.filter.return_value.all.return_value = [existing_association_1, existing_association_3]
        
        # Configure session.query to return different mocks based on the model
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
            
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_users_to_property(request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "Added 2 users to property 'Test Property'" in result.message
        assert "2 users were already associated" in result.message
        
        # Verify only 2 new associations were created (for users 2 and 4)
        assert self.mock_session.add.call_count == 2
        self.mock_session.commit.assert_called_once()
    
    def test_add_users_all_already_associated(self):
        """Test when all users are already associated"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[1, 2]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Mock existing associations for all users
        existing_association_1 = Mock(spec=PropertyAssociation)
        existing_association_1.user_id = 1
        existing_association_2 = Mock(spec=PropertyAssociation)
        existing_association_2.user_id = 2
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        association_query = Mock()
        association_query.filter.return_value.all.return_value = [existing_association_1, existing_association_2]
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_users_to_property(request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "All specified users are already associated with property 'Test Property'" in result.message
        
        # Verify no new associations were created
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()
    
    def test_add_users_empty_user_list(self):
        """Test with empty user list"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        association_query = Mock()
        association_query.filter.return_value.all.return_value = []
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_users_to_property(request)
        
        # Assert
        assert isinstance(result, PropertyResponse)
        assert "All specified users are already associated with property 'Test Property'" in result.message
        
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()
    
    def test_add_users_database_error(self):
        """Test when database commit fails"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[1, 2]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        association_query = Mock()
        association_query.filter.return_value.all.return_value = []
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Database error"):
            self.service.add_users_to_property(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding users to property: Database error")
    
    def test_add_users_logging_flow(self):
        """Test that logging works correctly"""
        # Arrange
        request = AddUsersPropertyRequest(
            property_id=123,
            user_ids=[1, 2]
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Reset the mock session to ensure clean state
        self.mock_session.reset_mock()
        self.mock_logger.reset_mock()
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        association_query = Mock()
        association_query.filter.return_value.all.return_value = []
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyAssociation:
                return association_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_users_to_property(request)
        
        # Assert
        self.mock_logger.info.assert_any_call("Adding users [1, 2] to property 123")
        self.mock_logger.info.assert_any_call("Successfully added 2 users to property 123")
        self.mock_logger.error.assert_not_called()
