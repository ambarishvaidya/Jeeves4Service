from ast import In
from unittest import mock
from pydantic import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date

from services.user_service.app.services.register_user import register_user
from services.user_service.app.dto.registration import RegisterUserRequest, RegisterUserResponse
from services.user_service.app.models.user import User
from services.user_service.app.models.family import Family

def test_register_user_success():
    """Test successful user registration"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_session.query.return_value.filter.return_value.first.return_value = None    
    mock_session.commit = Mock()    
    mock_session.add = Mock()
    
    # Mock flush to simulate database assigning ID to user
    def mock_flush():
        # Find the user object that was added and assign it an ID
        if mock_session.add.called:
            user_obj = mock_session.add.call_args[0][0]
            if hasattr(user_obj, 'id') and user_obj.id is None:
                user_obj.id = 123  # Simulate database-assigned ID
    
    mock_session.flush = Mock(side_effect=mock_flush)
    mock_logger = Mock()
    
    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1)
    )
    
    # Act
    response = register_user(request, mock_session, mock_logger)
    
    # Assert
    assert isinstance(response, RegisterUserResponse)
    assert response.user_id == 123  # Should match the mocked ID
    assert response.message == "User registration completed successfully"
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_logger.info.assert_called()

def test_register_user_duplicate_username():
    """Test registration with duplicate username"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    existing_user = User(first_name="John", last_name="Doe", email="other@example.com")
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Mock flush to simulate Integrity error
    def mock_flush():
        # Find the user object that was added and assign it an ID
        if mock_session.add.called:
            raise IntegrityError("User already exists", None, None)
    
    mock_session.flush = Mock(side_effect=mock_flush)

    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1)
    )

    # Act & Assert
    with pytest.raises(IntegrityError) as exc_info:
        register_user(request, mock_session, mock_logger)
    
    assert "User already exists" in str(exc_info.value)


def test_register_user_invalid_email():
    """Test registration with invalid email format"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    mock_session.add = Mock()
    
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


def test_register_user_weak_password():
    """Test registration with weak password"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    
    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="123",  # Too weak
        dob=date(1990, 1, 1)
    )
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        register_user(request, mock_session, mock_logger)
    
    assert exc_info is not None


def test_register_user_empty_first_name():
    """Test registration with empty first name"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    
    request = RegisterUserRequest(
        first_name="",
        last_name="Doe",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1)
    )
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        register_user(request, mock_session, mock_logger)
    
    assert exc_info is not None


def test_register_user_empty_last_name():
    """Test registration with empty last name"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    
    request = RegisterUserRequest(
        first_name="John",
        last_name="",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1)
    )
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        register_user(request, mock_session, mock_logger)
    
    assert exc_info is not None


def test_register_user_database_error():
    """Test registration with database error"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.commit.side_effect = IntegrityError("Database error", None, None)
    mock_session.rollback = Mock()
    
    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1)
    )
    
    # Act & Assert
    with pytest.raises(Exception):
        register_user(request, mock_session, mock_logger)
    
    mock_session.rollback.assert_called_once()


def test_register_user_with_additional_users():
    """Test registration with additional users"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.commit = Mock()
    mock_session.add = Mock()    
    
    def mock_flush():
        # Find the user object that was added and assign it an ID
        if mock_session.add.called:
            user_obj = mock_session.add.call_args[0][0]
            if hasattr(user_obj, 'id') and user_obj.id is None:
                user_obj.id = 123  # Simulate database-assigned ID
    
    mock_session.flush = Mock(side_effect=mock_flush)

    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="SecurePass123!",
        dob=date(1990, 1, 1),
        additional_users=[]
    )
    
    # Act
    response = register_user(request, mock_session, mock_logger)
    
    # Assert
    assert response.user_id is not None
    mock_session.add.assert_called()
    mock_session.commit.assert_called_once()


@pytest.mark.parametrize("invalid_email", [
    "invalid-email",
    "@example.com",
    "test@",
    "test.example.com",
    "test@.com",
    ""
])
def test_register_user_invalid_email_formats(invalid_email):
    """Test various invalid email formats"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_logger = Mock()
    mock_session.rollback = Mock()
    
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