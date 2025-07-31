import pytest
from unittest.mock import Mock
from app.dto.storage import PropertyStorageRequest, PropertyStorageResponse
from app.services.add_main_storage import AddMainStorage
from app.models.storage import Storage


class TestAddMainStorage:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_logger = Mock()
        self.mock_session = Mock()
        self.service = AddMainStorage(self.mock_logger, self.mock_session)
    
    def test_add_main_storage_success(self):
        """Test successful addition of main storage"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=None,
            storage_name="Wardrobe1"
        )
        
        # Mock the storage object that would be created
        mock_storage = Mock()
        mock_storage.id = 23
        mock_storage.storage_name = "Wardrobe1"
        
        # Mock session behavior
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        self.mock_session.commit.return_value = None
        
        # Act
        response = self.service.add_main_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "added successfully" in response.message
        assert "Wardrobe1" in response.message
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_add_main_storage_with_container_id_fails(self):
        """Test that main storage with container_id fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=99,  # Should be None for main storage
            storage_name="Invalid Main Storage"
        )
        
        # Act
        response = self.service.add_main_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "should not have a container_id" in response.message
        self.mock_session.add.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_add_main_storage_empty_name_fails(self):
        """Test that main storage with empty name fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=None,
            storage_name=""
        )
        
        # Act
        response = self.service.add_main_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Storage name is required" in response.message
        self.mock_session.add.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_add_main_storage_whitespace_name_fails(self):
        """Test that main storage with whitespace-only name fails"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=None,
            storage_name="   "
        )
        
        # Act
        response = self.service.add_main_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Storage name is required" in response.message
        self.mock_session.add.assert_not_called()
    
    def test_add_main_storage_database_error(self):
        """Test database error handling for main storage"""
        # Arrange
        request = PropertyStorageRequest(
            property_id=1,
            room_id=3,
            container_id=None,
            storage_name="Wardrobe1"
        )
        
        # Mock database error
        self.mock_session.commit.side_effect = Exception("Database connection failed")
        
        # Act
        response = self.service.add_main_storage(request)
        
        # Assert
        assert isinstance(response, PropertyStorageResponse)
        assert "Failed to add main storage" in response.message
        assert "Database connection failed" in response.message
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
