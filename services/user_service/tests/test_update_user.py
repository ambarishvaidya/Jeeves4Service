from unittest import mock
from pydantic import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import date

from services.user_service.app.services.update_user import UpdateUserService
from services.user_service.app.models.user import User


class TestUpdateUserService:
    """Test class for UpdateUserService with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        
        # Create service instance with mocked dependencies
        self.service = UpdateUserService(
            logger=self.mock_logger,
            session=self.mock_session
        )
    
    def test_update_user_success_single_field(self):
        """Test successful update of a single user field"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.email = "john.doe@example.com"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"first_name": "Johnny"}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.first_name == "Johnny"
        
        # Verify interactions
        self.mock_session.query.assert_called_once_with(User)
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_any_call("Starting user update for user ID: 123")
        self.mock_logger.info.assert_any_call("Updated first_name for user ID: 123")
        self.mock_logger.info.assert_any_call("Successfully updated user ID: 123")
    
    def test_update_user_success_multiple_fields(self):
        """Test successful update of multiple user fields"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 456
        mock_user.first_name = "Jane"
        mock_user.last_name = "Smith"
        mock_user.email = "jane.smith@example.com"
        mock_user.is_active = True
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {
            "first_name": "Janet",
            "last_name": "Johnson",
            "is_active": False
        }
        
        # Act
        result = self.service.update_user(456, updates)
        
        # Assert
        assert result == {"user_id": 456, "message": "User updated successfully"}
        assert mock_user.first_name == "Janet"
        assert mock_user.last_name == "Johnson"
        assert mock_user.is_active == False
        
        # Verify all fields were logged as updated
        self.mock_logger.info.assert_any_call("Updated first_name for user ID: 456")
        self.mock_logger.info.assert_any_call("Updated last_name for user ID: 456")
        self.mock_logger.info.assert_any_call("Updated is_active for user ID: 456")
    
    def test_update_user_not_found(self):
        """Test update when user does not exist"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        updates = {"first_name": "NewName"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            self.service.update_user(999, updates)
        
        # Verify interactions
        self.mock_session.query.assert_called_once_with(User)
        self.mock_session.commit.assert_not_called()
        self.mock_logger.info.assert_called_once_with("Starting user update for user ID: 999")
        self.mock_logger.error.assert_called_once_with("User with ID 999 not found")
    
    def test_update_user_invalid_field(self):
        """Test update with invalid field name that doesn't exist on User model"""
        # Arrange - Create a controlled mock that simulates real User behavior
        class MockUser:
            def __init__(self):
                self.id = 123
                self.first_name = "John"
                
        mock_user = MockUser()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"invalid_field": "some_value", "first_name": "Johnny"}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.first_name == "Johnny"
        # invalid_field should not be set since hasattr returned False
        assert not hasattr(mock_user, "invalid_field")
        
        # Verify only valid field was logged as updated
        self.mock_logger.info.assert_any_call("Updated first_name for user ID: 123")
        # Invalid field should not be logged
        assert not any("invalid_field" in str(call) for call in self.mock_logger.info.call_args_list)
    
    def test_update_user_empty_updates(self):
        """Test update with empty updates dictionary"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_any_call("Starting user update for user ID: 123")
        self.mock_logger.info.assert_any_call("Successfully updated user ID: 123")
    
    def test_update_user_date_field(self):
        """Test updating date field (date of birth)"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.dob = date(1990, 1, 1)
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        new_dob = date(1985, 5, 15)
        updates = {"dob": new_dob}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.dob == new_dob
        self.mock_logger.info.assert_any_call("Updated dob for user ID: 123")
    
    def test_update_user_boolean_field(self):
        """Test updating boolean fields (is_admin, is_active)"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.is_admin = False
        mock_user.is_active = True
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"is_admin": True, "is_active": False}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.is_admin == True
        assert mock_user.is_active == False
        self.mock_logger.info.assert_any_call("Updated is_admin for user ID: 123")
        self.mock_logger.info.assert_any_call("Updated is_active for user ID: 123")
    
    def test_update_user_database_exception(self):
        """Test handling of database exception during commit"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.first_name = "John"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit.side_effect = Exception("Database connection lost")
        self.mock_session.rollback = Mock()
        
        updates = {"first_name": "Johnny"}
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection lost"):
            self.service.update_user(123, updates)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_with("Error during user update: Database connection lost")
    
    def test_update_user_query_exception(self):
        """Test handling of exception during user query"""
        # Arrange
        self.mock_session.query.side_effect = Exception("Query failed")
        self.mock_session.rollback = Mock()
        
        updates = {"first_name": "Johnny"}
        
        # Act & Assert
        with pytest.raises(Exception, match="Query failed"):
            self.service.update_user(123, updates)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_with("Error during user update: Query failed")
    
    def test_update_user_email_field(self):
        """Test updating email field"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "old@example.com"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"email": "new@example.com"}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.email == "new@example.com"
        self.mock_logger.info.assert_any_call("Updated email for user ID: 123")
    
    def test_update_user_none_values(self):
        """Test updating fields with None values"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.dob = date(1990, 1, 1)
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"dob": None}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.dob is None
        self.mock_logger.info.assert_any_call("Updated dob for user ID: 123")
    
    def test_update_user_protected_fields(self):
        """Test updating protected fields like password_hash and salt"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.password_hash = b"old_hash"
        mock_user.salt = b"old_salt"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {
            "password_hash": b"new_hash",
            "salt": b"new_salt"
        }
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.password_hash == b"new_hash"
        assert mock_user.salt == b"new_salt"
        self.mock_logger.info.assert_any_call("Updated password_hash for user ID: 123")
        self.mock_logger.info.assert_any_call("Updated salt for user ID: 123")
    
    def test_update_user_zero_user_id(self):
        """Test update with user ID of 0"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        updates = {"first_name": "Test"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            self.service.update_user(0, updates)
        
        self.mock_logger.error.assert_called_once_with("User with ID 0 not found")
    
    def test_update_user_negative_user_id(self):
        """Test update with negative user ID"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        updates = {"first_name": "Test"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            self.service.update_user(-1, updates)
        
        self.mock_logger.error.assert_called_once_with("User with ID -1 not found")
    
    def test_update_user_logging_sequence(self):
        """Test the complete logging sequence for successful update"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {"first_name": "Johnny", "last_name": "Davis"}
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert logging sequence
        expected_calls = [
            mock.call("Starting user update for user ID: 123"),
            mock.call("Updated first_name for user ID: 123"),
            mock.call("Updated last_name for user ID: 123"),
            mock.call("Successfully updated user ID: 123")
        ]
        
        self.mock_logger.info.assert_has_calls(expected_calls, any_order=False)
        
        # Verify final result
        assert result == {"user_id": 123, "message": "User updated successfully"}
    
    def test_update_user_mixed_valid_invalid_fields(self):
        """Test update with mixture of valid and invalid field names"""
        # Arrange - Create a controlled mock with only specific attributes
        class MockUser:
            def __init__(self):
                self.id = 123
                self.first_name = "John"
                self.email = "john@example.com"
                self.last_name = "Doe"
                
        mock_user = MockUser()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_session.commit = Mock()
        
        updates = {
            "first_name": "Johnny",      # Valid
            "invalid_field": "value",    # Invalid - not defined on MockUser
            "email": "new@example.com",  # Valid
            "another_invalid": "test"    # Invalid - not defined on MockUser
        }
        
        # Act
        result = self.service.update_user(123, updates)
        
        # Assert
        assert result == {"user_id": 123, "message": "User updated successfully"}
        assert mock_user.first_name == "Johnny"
        assert mock_user.email == "new@example.com"
        
        # Verify only valid fields were logged
        self.mock_logger.info.assert_any_call("Updated first_name for user ID: 123")
        self.mock_logger.info.assert_any_call("Updated email for user ID: 123")
        
        # Verify invalid fields were not logged
        info_calls = [str(call) for call in self.mock_logger.info.call_args_list]
        assert not any("invalid_field" in call for call in info_calls)
        assert not any("another_invalid" in call for call in info_calls)
        
        # Verify invalid fields were not set on the mock object
        assert not hasattr(mock_user, "invalid_field")
        assert not hasattr(mock_user, "another_invalid")
