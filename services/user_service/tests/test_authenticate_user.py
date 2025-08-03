from unittest import mock
from pydantic import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import date

from services.user_service.app.services.authenticate_user import AuthenticateUser
from services.user_service.app.dto.user import AuthenticateUserResponse
from services.user_service.app.models.user import User


class TestAuthenticateUser:
    """Test class for AuthenticateUser service with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        self.mock_crypto_service = Mock()
        
        # Create service instance with mocked dependencies
        self.service = AuthenticateUser(
            logger=self.mock_logger,
            session=self.mock_session,
            crypto_service=self.mock_crypto_service
        )
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        mock_user.is_admin = False
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.return_value = True
        
        # Act
        with patch('secrets.token_hex', return_value='mocked_session_id'):
            result = self.service.authenticate("john.doe@example.com", "password123")
        
        # Assert
        assert isinstance(result, AuthenticateUserResponse)
        assert result.session_id == "mocked_session_id"
        assert result.user_id == 123
        assert result.email == "john.doe@example.com"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.is_admin == False
        
        # Verify interactions
        self.mock_session.query.assert_called_once_with(User)
        self.mock_crypto_service.assert_called_once_with(
            "hashed_password", "password123", "salt123"
        )
        self.mock_logger.info.assert_any_call("Starting authentication for email: john.doe@example.com")
        self.mock_logger.info.assert_any_call("User with email john.doe@example.com authenticated successfully")
    
    def test_authenticate_user_not_found(self):
        """Test authentication when user does not exist"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            self.service.authenticate("nonexistent@example.com", "password123")
        
        # Verify interactions
        self.mock_session.query.assert_called_once_with(User)
        self.mock_crypto_service.verify_password.assert_not_called()
        self.mock_logger.info.assert_called_once_with("Starting authentication for email: nonexistent@example.com")
        self.mock_logger.error.assert_called_once_with("User with email nonexistent@example.com not found")
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid password"):
            self.service.authenticate("john.doe@example.com", "wrong_password")
        
        # Verify interactions
        self.mock_session.query.assert_called_once_with(User)
        self.mock_crypto_service.assert_called_once_with(
            "hashed_password", "wrong_password", "salt123"
        )
        self.mock_logger.info.assert_called_once_with("Starting authentication for email: john.doe@example.com")
        self.mock_logger.error.assert_called_once_with("Invalid password")
    
    def test_authenticate_admin_user_success(self):
        """Test successful authentication for admin user"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 456
        mock_user.email = "admin@example.com"
        mock_user.first_name = "Admin"
        mock_user.last_name = "User"
        mock_user.password_hash = "admin_hashed_password"
        mock_user.salt = "admin_salt"
        mock_user.is_admin = True
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.verify_password.return_value = True
        
        # Act
        with patch('secrets.token_hex', return_value='admin_session_id'):
            result = self.service.authenticate("admin@example.com", "admin_password")
        
        # Assert
        assert isinstance(result, AuthenticateUserResponse)
        assert result.session_id == "admin_session_id"
        assert result.user_id == 456
        assert result.email == "admin@example.com"
        assert result.first_name == "Admin"
        assert result.last_name == "User"
        assert result.is_admin == True
    
    def test_authenticate_empty_email(self):
        """Test authentication with empty email"""
        # Act & Assert
        with pytest.raises(Exception):  # Will depend on how your system handles empty strings
            self.service.authenticate("", "password123")
    
    def test_authenticate_empty_password(self):
        """Test authentication with empty password"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid password"):
            self.service.authenticate("john.doe@example.com", "")
        
        # Verify password verification was called with empty password
        self.mock_crypto_service.assert_called_once_with(
            "hashed_password", "", "salt123"
        )
    
    def test_authenticate_database_exception(self):
        """Test authentication when database query raises exception"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            self.service.authenticate("john.doe@example.com", "password123")
        
        # Verify error was logged
        self.mock_logger.error.assert_called_with("Error during authentication: Database error")
    
    def test_authenticate_crypto_service_exception(self):
        """Test authentication when crypto service raises exception"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.side_effect = Exception("Crypto error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Crypto error"):
            self.service.authenticate("john.doe@example.com", "password123")
        
        # Verify error was logged
        self.mock_logger.error.assert_called_with("Error during authentication: Crypto error")
    
    def test_authenticate_session_id_generation(self):
        """Test that each authentication generates a unique session ID"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        mock_user.is_admin = False
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.return_value = True
        
        # Act - authenticate twice
        with patch('secrets.token_hex', side_effect=['session_id_1', 'session_id_2']):
            result1 = self.service.authenticate("john.doe@example.com", "password123")
            result2 = self.service.authenticate("john.doe@example.com", "password123")
        
        # Assert - different session IDs
        assert result1.session_id == "session_id_1"
        assert result2.session_id == "session_id_2"
        assert result1.session_id != result2.session_id
    
    def test_authenticate_case_sensitive_email(self):
        """Test that email authentication is case sensitive (or insensitive based on your requirements)"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.email = "john.doe@example.com"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.password_hash = "hashed_password"
        mock_user.salt = "salt123"
        mock_user.is_admin = False
        
        # Test case: exact match should work
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_crypto_service.verify_password.return_value = True
        
        # Act
        with patch('secrets.token_hex', return_value='session_id'):
            result = self.service.authenticate("john.doe@example.com", "password123")
        
        # Assert
        assert result.email == "john.doe@example.com"
        
        # Test case: different case - this should fail if your system is case-sensitive
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="User not found"):
            self.service.authenticate("JOHN.DOE@EXAMPLE.COM", "password123")
