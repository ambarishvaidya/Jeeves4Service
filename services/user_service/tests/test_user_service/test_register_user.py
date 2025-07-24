from unittest import mock
from pydantic import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date

from services.user_service.app.services.register_user import RegisterUserService
from services.user_service.app.dto.registration import RegisterUserRequest, RegisterUserResponse
from services.user_service.app.models.user import User


class TestRegisterUserService:
    """Test class for RegisterUserService with dependency injection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.mock_logger = Mock()
        self.mock_crypto_service = Mock()
        
        # Create service instance with mocked dependencies
        self.service = RegisterUserService(
            logger=self.mock_logger,
            session=self.mock_session,
            crypto_hash_service=self.mock_crypto_service
        )
    
    def test_register_user_success(self):
        """Test successful user registration"""
        # Arrange
        self.mock_session.query.return_value.filter.return_value.first.return_value = None    
        self.mock_session.commit = Mock()    
        self.mock_session.add = Mock()
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        # Mock flush to simulate database assigning ID to user
        def mock_flush():
            # Find the user object that was added and assign it an ID
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123  # Simulate database-assigned ID
        
        self.mock_session.flush = Mock(side_effect=mock_flush)
        
        request = RegisterUserRequest(
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)
        )
        
        # Act
        response = self.service.register_user(request)
        
        # Assert
        assert isinstance(response, RegisterUserResponse)
        assert response.user_id == 123  # Should match the mocked ID
        assert response.message == "User registration completed successfully"
        self.mock_session.add.assert_called()
        self.mock_session.flush.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_logger.info.assert_called()
        self.mock_crypto_service.assert_called_with("SecurePass123!")

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        # Arrange
        existing_user = User(first_name="John", last_name="Doe", email="other@example.com")
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        # Mock flush to simulate Integrity error
        def mock_flush():
            # Find the user object that was added and assign it an ID
            if self.mock_session.add.called:
                raise IntegrityError("User already exists", None, None)
        
        self.mock_session.flush = Mock(side_effect=mock_flush)

        request = RegisterUserRequest(
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)
        )

        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            self.service.register_user(request)
        
        assert "User already exists" in str(exc_info.value)

    def test_register_user_invalid_email(self):
        """Test registration with invalid email format"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            request = RegisterUserRequest(
                first_name="John",
                last_name="Doe",
                email="invalid-email",
                password="SecurePass123!",
                dob=date(1990, 1, 1)
            )
        
        assert exc_info is not None

    def test_register_user_weak_password(self):
        """Test registration with weak password"""
        request = RegisterUserRequest(
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="123",  # Too weak
            dob=date(1990, 1, 1)
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.register_user(request)
        
        assert "Password must be at least 8 characters long" in str(exc_info.value)

    def test_register_user_empty_first_name(self):
        """Test registration with empty first name"""
        request = RegisterUserRequest(
            first_name="",
            last_name="Doe",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.register_user(request)
        
        assert "First name cannot be empty" in str(exc_info.value)

    def test_register_user_empty_last_name(self):
        """Test registration with empty last name"""
        request = RegisterUserRequest(
            first_name="John",
            last_name="",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.register_user(request)
        
        assert "Last name cannot be empty" in str(exc_info.value)

    def test_register_user_database_error(self):
        """Test registration with database error"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_session.commit.side_effect = IntegrityError("Database error", None, None)
        self.mock_session.rollback = Mock()
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        request = RegisterUserRequest(
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)
        )
        
        # Act & Assert
        with pytest.raises(Exception):
            self.service.register_user(request)
        
        self.mock_session.rollback.assert_called_once()

    def test_register_user_with_additional_users(self):
        """Test registration with additional users"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_session.commit = Mock()
        self.mock_session.add = Mock()
        self.mock_crypto_service.return_value = ("hashed_password", "salt123")
        
        def mock_flush():
            # Find the user object that was added and assign it an ID
            if self.mock_session.add.called:
                user_obj = self.mock_session.add.call_args[0][0]
                if hasattr(user_obj, 'id') and user_obj.id is None:
                    user_obj.id = 123  # Simulate database-assigned ID
        
        self.mock_session.flush = Mock(side_effect=mock_flush)

        request = RegisterUserRequest(
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="SecurePass123!",
            dob=date(1990, 1, 1)            
        )
        
        # Act
        response = self.service.register_user(request)
        
        # Assert
        assert response.user_id is not None
        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called_once()

    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@example.com",
        "test@",
        "test.example.com",
        "test@.com",
        ""
    ])
    def test_register_user_invalid_email_formats(self, invalid_email):
        """Test various invalid email formats"""
        self.mock_session.rollback = Mock()
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            request = RegisterUserRequest(
                first_name="John",
                last_name="Doe",
                email=invalid_email,
                password="SecurePass123!",
                dob=date(1990, 1, 1)
            )
        
        assert exc_info is not None



    
