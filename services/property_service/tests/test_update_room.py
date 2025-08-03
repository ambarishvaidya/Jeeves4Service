from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.property_service.app.services.update_room import UpdateRoom
from services.property_service.app.dto.property import UpdateRoomRequest, RoomResponse
from services.property_service.app.models.property import PropertyRooms


class TestUpdateRoom:
    """Test class for UpdateRoom service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = UpdateRoom(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_update_room_success(self):
        """Test successful room name update"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Updated Master Bedroom"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Master Bedroom"
        
        # Setup query mocks - first for finding the room, second for checking duplicates
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None  # No duplicate
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query  # First call to find the room
            else:
                return room_duplicate_query  # Second call to check duplicates
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.update_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Updated Master Bedroom" in result.message
        assert "Old Master Bedroom" in result.message
        assert result.room_id == 123
        assert mock_room.room_name == "Updated Master Bedroom"
        
        # Verify database operations
        self.mock_session.commit.assert_called_once()
    
    def test_update_room_not_found(self):
        """Test when room does not exist"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=999,
            room_name="New Name"
        )
        
        room_query = Mock()
        room_query.filter.return_value.first.return_value = None
        
        self.mock_session.query.return_value = room_query
        
        # Act & Assert
        with pytest.raises(ValueError, match="Room with ID 999 not found"):
            self.service.update_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_update_room_duplicate_name(self):
        """Test when new room name already exists in property"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Living Room"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Bedroom"
        
        mock_existing_room = Mock(spec=PropertyRooms)
        mock_existing_room.id = 789
        mock_existing_room.room_name = "Living Room"
        
        # Setup query mocks
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = mock_existing_room
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act & Assert
        with pytest.raises(ValueError, match="Room name 'Living Room' already exists in this property"):
            self.service.update_room(request)
        
        # Verify rollback and no commit
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
        assert mock_room.room_name == "Bedroom"  # Unchanged
    
    def test_update_room_same_name(self):
        """Test when new name is the same as current name"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Same Room Name"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Same Room Name"
        
        # Setup query mocks - first for finding the room, second for checking duplicates
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None  # No duplicate (not needed but for consistency)
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query  # First call to find the room
            else:
                return room_duplicate_query  # Second call to check duplicates (won't be reached)
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.update_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Room name is already 'Same Room Name'. No update needed." in result.message
        assert result.room_id == 123
        
        # Verify no commit was called
        self.mock_session.commit.assert_not_called()
    
    def test_update_room_empty_name(self):
        """Test updating room to empty name"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name=""
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Name"
        
        # Setup query mocks
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.update_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert mock_room.room_name == ""
        self.mock_session.commit.assert_called_once()
    
    def test_update_room_database_error(self):
        """Test when database commit fails"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Error Room"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Name"
        
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError, match="Database error"):
            self.service.update_room(request)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_once_with("Error updating room: Database error")
    
    def test_update_room_with_special_characters(self):
        """Test updating room with special characters in name"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Master Bedroom & Bath #1"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Room"
        
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.update_room(request)
        
        # Assert
        assert isinstance(result, RoomResponse)
        assert "Master Bedroom & Bath #1" in result.message
        assert mock_room.room_name == "Master Bedroom & Bath #1"
    
    def test_update_room_duplicate_with_different_room_in_same_property(self):
        """Test duplicate detection excludes the current room"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Kitchen"
        )
        
        # Current room being updated
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Kitchen"
        
        # Another room with same name but different ID (should trigger duplicate error)
        mock_existing_room = Mock(spec=PropertyRooms)
        mock_existing_room.id = 789  # Different ID
        mock_existing_room.property_id = 456  # Same property
        mock_existing_room.room_name = "Kitchen"
        
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = mock_existing_room
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act & Assert
        with pytest.raises(ValueError, match="Room name 'Kitchen' already exists in this property"):
            self.service.update_room(request)
        
        self.mock_session.rollback.assert_called_once()
        self.mock_session.commit.assert_not_called()
    
    def test_update_room_logging_flow(self):
        """Test that logging works correctly"""
        # Arrange
        request = UpdateRoomRequest(
            room_id=123,
            room_name="Logging Test Room"
        )
        
        mock_room = Mock(spec=PropertyRooms)
        mock_room.id = 123
        mock_room.property_id = 456
        mock_room.room_name = "Old Name"
        
        room_find_query = Mock()
        room_find_query.filter.return_value.first.return_value = mock_room
        
        room_duplicate_query = Mock()
        room_duplicate_query.filter.return_value.first.return_value = None
        
        query_call_count = 0
        def query_side_effect(model):
            nonlocal query_call_count
            query_call_count += 1
            if query_call_count == 1:
                return room_find_query
            else:
                return room_duplicate_query
                
        self.mock_session.query.side_effect = query_side_effect
        
        # Act
        result = self.service.update_room(request)
        
        # Assert
        self.mock_logger.info.assert_any_call("Updating room 123 to name 'Logging Test Room'")
        self.mock_logger.info.assert_any_call("Room 123 updated successfully from 'Old Name' to 'Logging Test Room'")
        self.mock_logger.error.assert_not_called()
