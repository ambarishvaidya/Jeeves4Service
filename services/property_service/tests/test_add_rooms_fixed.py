from unittest import mock
from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.property_service.app.services.add_rooms import AddRooms
from services.property_service.app.dto.property import PropertyRoomRequest, RoomResponse
from services.property_service.app.models.property import Property, PropertyRooms


class TestAddRooms:
    """Test class for AddRooms service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = AddRooms(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_add_room_success(self):
        """Test successful room addition"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Master Bedroom"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None  # No existing room
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Master Bedroom" in result.message
        assert "Test Property" in result.message
        
        # Verify database operations
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
    
    def test_add_room_property_not_found(self):
        """Test when property does not exist"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=999,
            room_name="Non-existent Room"
        )
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = None  # Property not found
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return Mock()  # This shouldn't be called
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act & Assert
        with pytest.raises(ValueError, match="Property with ID 999 not found"):
            self.service.add_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_add_room_duplicate_name(self):
        """Test when room name already exists in property"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Duplicate Room"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        mock_existing_room = Mock(spec=PropertyRooms)
        mock_existing_room.id = 789
        mock_existing_room.room_name = "Duplicate Room"
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = mock_existing_room  # Room exists
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act & Assert
        with pytest.raises(ValueError, match="Room 'Duplicate Room' already exists in property 'Test Property'"):
            self.service.add_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_add_room_empty_name(self):
        """Test adding room with empty name"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name=""
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Test Property" in result.message
        
        # Verify database operations
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
    
    def test_add_room_database_error_on_add(self):
        """Test when database add fails"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Error Room"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        self.mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Database error"):
            self.service.add_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding room to property 123: Database error")
    
    def test_add_room_database_error_on_flush(self):
        """Test when database flush fails"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Flush Error Room"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        self.mock_session.flush.side_effect = SQLAlchemyError("Flush error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Flush error"):
            self.service.add_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding room to property 123: Flush error")
    
    def test_add_room_database_error_on_commit(self):
        """Test when database commit fails"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Commit Error Room"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        self.mock_session.commit.side_effect = SQLAlchemyError("Commit error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Commit error"):
            self.service.add_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error adding room to property 123: Commit error")
    
    def test_add_room_with_special_characters(self):
        """Test adding room with special characters in name"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Master Bedroom & Bath #1"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        # Setup query mocks
        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.add_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Master Bedroom & Bath #1" in result.message
        assert "Test Property" in result.message
        
        # Verify database operations
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
    
    def test_add_room_logging_flow(self):
        """Test that logging works correctly"""
        # Arrange
        request = PropertyRoomRequest(
            property_id=123,
            room_name="Logging Test Room"
        )
        
        mock_property = Mock(spec=Property)
        mock_property.id = 123
        mock_property.name = "Test Property"
        
        mock_room = Mock(spec=PropertyRooms)        

        property_query = Mock()
        property_query.filter.return_value.first.return_value = mock_property
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        
        def query_side_effect(model):
            if model == Property:
                return property_query
            elif model == PropertyRooms:
                return room_query
            return Mock()  # fallback for any unexpected models
                
        self.mock_session.query.side_effect = query_side_effect

        def add_side_effect(room_obj):
            # Assign ID to the room object when it's added
            room_obj.id = 456

        self.mock_session.add.side_effect = add_side_effect

        # Act
        result = self.service.add_room(request)
        
        # Assert
        self.mock_logger.info.assert_any_call("Room 'Logging Test Room' added successfully to property 123 with ID 456")
        self.mock_logger.error.assert_not_called()
