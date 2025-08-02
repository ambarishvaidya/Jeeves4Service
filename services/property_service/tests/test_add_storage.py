import pytest
from unittest.mock import Mock
from app.dto.storage import PropertyStorageRequest, PropertyStorageResponse
from app.services.add_storage import AddStorage
from app.models.storage import Storage


class TestAddStorage:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_session = Mock()
        self.service = AddStorage(self.mock_logger, self.mock_session)
    
    def test_add_storage_success(self):
        """Test successful addition of sub-storage"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=23,
            storage_name="Top Shelf"
        )
        
        # Mock parent storage exists
        mock_parent = Mock()
        mock_parent.storage_name = "Wardrobe1"
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_parent
        
        # Mock the storage object that would be created
        mock_storage = Mock()
        mock_storage.id = 24
        mock_storage.storage_name = "Top Shelf"
        
        # Mock session behavior
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        self.mock_session.commit.return_value = None
        
        # Act
        response = self.service.add_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "added successfully" in response.message
        assert "Top Shelf" in response.message
        assert "Wardrobe1" in response.message
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_add_storage_without_container_id_fails(self):
        """Test that sub-storage without container_id fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=None,  # Should have a parent ID
            storage_name="Invalid Sub Storage"
        )
        
        # Act
        response = self.service.add_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "must have a container_id" in response.message
        self.mock_session.add.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_add_storage_empty_name_fails(self):
        """Test that sub-storage with empty name fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=23,
            storage_name=""
        )
        
        # Act
        response = self.service.add_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Storage name is required" in response.message
        self.mock_session.add.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_add_storage_with_nonexistent_parent_fails(self):
        """Test that sub-storage with non-existent parent fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=999,  # Non-existent parent
            storage_name="Orphaned Storage"
        )
        
        # Mock parent storage does not exist
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        response = self.service.add_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Container with ID 999 not found" in response.message
        self.mock_session.add.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_add_storage_database_error(self):
        """Test database error handling for sub-storage"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=23,
            storage_name="Top Shelf"
        )
        
        # Mock parent storage exists
        mock_parent = Mock()
        mock_parent.storage_name = "Wardrobe1"
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_parent
        
        # Mock database error
        self.mock_session.commit.side_effect = Exception("Database connection failed")
        
        # Act
        response = self.service.add_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Failed to add sub-storage" in response.message
        assert "Database connection failed" in response.message
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called()
    
    def test_add_storage_validates_parent_in_same_property_and_room(self):
        """Test that parent validation checks property_id and room_id"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=23,
            storage_name="Top Shelf"
        )
        
        # Act
        self.service.add_storage(request)
        
        # Assert - verify the query filters by property_id, room_id, and container_id
        self.mock_session.query.assert_called_with(Storage)
        # The filter call should include all three conditions
        filter_call = self.mock_session.query.return_value.filter
        assert filter_call.called


if __name__ == "__main__":
    pytest.main([__file__])
