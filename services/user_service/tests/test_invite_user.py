from unittest import mock
from pydantic import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from psycopg2 import IntegrityError
from datetime import date

from services.user_service.app.services.invite_user import InviteUserService
from services.user_service.app.dto.user import InviteUser
from services.user_service.app.models.user import User, UserPassword


class TestInviteUserService:
    """Test class for InviteUserService with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        self.mock_crypto_service = Mock()
        
        # Create service instance with mocked dependencies
        self.service = InviteUserService(
            logger=self.mock_logger,
            session=self.mock_session,
            crypto_hash_service=self.mock_crypto_service
        )
    
    def test_send_invite_single_user_success(self):
        """Test successful invitation of a single user"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        # Mock flush to simulate database assigning ID to user
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit = Mock()
        
        invite_users = [
            InviteUser(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com"
            )
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'a'):  # Mock password generation
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "All 1 users invited successfully"
        
        # Verify interactions
        assert self.mock_session.add.call_count == 2  # User and UserPassword
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_crypto_service.assert_called_once_with("aaaaaaaa")  # 8 'a's from mocked choice
        self.mock_logger.info.assert_any_call("Starting invite user process")
        self.mock_logger.info.assert_any_call("Successfully invited user: john.doe@example.com")
    
    def test_send_invite_multiple_users_success(self):
        """Test successful invitation of multiple users"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        # Mock flush to simulate database assigning IDs
        user_id_counter = [100]  # Use list to allow modification in nested function
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = user_id_counter[0]
                    user_id_counter[0] += 1
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john.doe@example.com"),
            InviteUser(first_name="Jane", last_name="Smith", email="jane.smith@example.com"),
            InviteUser(first_name="Bob", last_name="Johnson", email="bob.johnson@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'a'):
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "All 3 users invited successfully"
        assert self.mock_session.add.call_count == 6  # 3 users + 3 UserPasswords
        assert self.mock_session.commit.call_count == 3  # One commit per user
        assert self.mock_crypto_service.call_count == 3
    
    def test_send_invite_integrity_error_single_user(self):
        """Test handling of IntegrityError for single user (duplicate email)"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        self.mock_session.flush.side_effect = IntegrityError("Duplicate email", None, None)
        self.mock_session.rollback = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="duplicate@example.com")
        ]
        
        # Act
        result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "Failed to invite all 1 users"
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_with(
            "Error inviting user duplicate@example.com: Duplicate email"
        )
    
    def test_send_invite_partial_success(self):
        """Test partial success scenario - some users succeed, some fail"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        # Mock to succeed for first user, fail for second, succeed for third
        call_count = [0]  # Use list to track calls
        def mock_flush_side_effect():
            call_count[0] += 1
            if call_count[0] == 2:  # Second user fails
                raise IntegrityError("Duplicate email", None, None)
            # First and third users succeed
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 100 + call_count[0]
        
        self.mock_session.flush = Mock(side_effect=mock_flush_side_effect)
        self.mock_session.commit = Mock()
        self.mock_session.rollback = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john@example.com"),
            InviteUser(first_name="Jane", last_name="Smith", email="duplicate@example.com"),
            InviteUser(first_name="Bob", last_name="Johnson", email="bob@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'a'):
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert "Invited 2 users successfully, 1 failed" in result
        assert "duplicate@example.com" in result
        assert self.mock_session.commit.call_count == 2  # Two successful commits
        assert self.mock_session.rollback.call_count == 1  # One rollback for failed user
    
    def test_send_invite_empty_list(self):
        """Test inviting empty list of users"""
        # Act
        result = self.service.send_invite([])
        
        # Assert
        assert result == "All 0 users invited successfully"
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()
    
    def test_send_invite_crypto_service_exception(self):
        """Test handling of crypto service exception"""
        # Arrange
        self.mock_crypto_service.side_effect = Exception("Crypto error")
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john@example.com")
        ]
        
        # Act
        result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "Failed to invite all 1 users"
        self.mock_logger.error.assert_called_with(
            "Unexpected error inviting user john@example.com: Crypto error"
        )
        self.mock_session.rollback.assert_called_once()
    
    def test_send_invite_password_generation(self):
        """Test that passwords are generated correctly"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']):
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "All 1 users invited successfully"
        self.mock_crypto_service.assert_called_once_with("abcdefgh")
    
    def test_send_invite_user_model_creation(self):
        """Test that User and UserPassword models are created correctly"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 456
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit = Mock()
        
        invite_users = [
            InviteUser(first_name="Alice", last_name="Wonder", email="alice@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'x'):
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "All 1 users invited successfully"
        
        # Verify User model creation
        user_calls = [call for call in self.mock_session.add.call_args_list 
                     if isinstance(call[0][0], User)]
        assert len(user_calls) == 1
        
        user_obj = user_calls[0][0][0]
        assert user_obj.first_name == "Alice"
        assert user_obj.last_name == "Wonder"
        assert user_obj.email == "alice@example.com"
        assert user_obj.password_hash == "hashed_password"
        assert user_obj.salt == "salt123"
        assert user_obj.is_admin == False
        assert user_obj.dob == date.min
        
        # Verify UserPassword model creation
        password_calls = [call for call in self.mock_session.add.call_args_list 
                         if isinstance(call[0][0], UserPassword)]
        assert len(password_calls) == 1
        
        password_obj = password_calls[0][0][0]
        assert password_obj.user_id == 456
        assert password_obj.email == "alice@example.com"
        assert password_obj.password_str == "xxxxxxxx"
    
    def test_send_invite_database_commit_exception(self):
        """Test handling of exception during commit"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit.side_effect = Exception("Database connection lost")
        self.mock_session.rollback = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'a'):
            result = self.service.send_invite(invite_users)
        
        # Assert
        assert result == "Failed to invite all 1 users"
        self.mock_session.rollback.assert_called_once()
        self.mock_logger.error.assert_called_with(
            "Unexpected error inviting user john@example.com: Database connection lost"
        )
    
    def test_send_invite_invalid_email_format(self):
        """Test handling of invalid email format in InviteUser"""
        # This test verifies that Pydantic validation works
        with pytest.raises(ValidationError):
            InviteUser(first_name="John", last_name="Doe", email="invalid-email")
    
    def test_send_invite_logging_behavior(self):
        """Test that appropriate logging occurs"""
        # Arrange
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        def mock_flush():
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        self.mock_session.commit = Mock()
        
        invite_users = [
            InviteUser(first_name="John", last_name="Doe", email="john@example.com")
        ]
        
        # Act
        with patch('secrets.choice', side_effect=lambda x: 'a'):
            self.service.send_invite(invite_users)
        
        # Assert
        self.mock_logger.info.assert_any_call("Starting invite user process")
        self.mock_logger.info.assert_any_call("Successfully invited user: john@example.com")
        
        # Verify no error logging for successful case
        self.mock_logger.error.assert_not_called()
