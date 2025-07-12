import services.shared.j4s_crypto_lib.password_processor as password_processor
import pytest

"""Write tests for the password_processor module."""
def test_generate_salt():
    salt = password_processor.generate_salt()
    assert isinstance(salt, bytes)
    assert len(salt) == 32  # 16 bytes hex encoded is 32 characters

def test_generate_hash():
    password = "test_password"
    hashed_password, salt = password_processor.generate_hash(password)
    assert isinstance(hashed_password, bytes)
    assert isinstance(salt, bytes)
    assert len(salt) == 32  # 16 bytes hex encoded is 32 characters
    assert len(hashed_password) == 32  # SHA-256 produces a 32-byte hash


def test_verify_password():
    password = "test_password"
    hashed_password, salt = password_processor.generate_hash(password)
    
    # Test with correct password
    assert password_processor.verify_password(hashed_password, password, salt) is True
    
    # Test with incorrect password
    assert password_processor.verify_password(hashed_password, "wrong_password", salt) is False
    
    # Test with empty password
    assert password_processor.verify_password(hashed_password, "", salt) is False    
