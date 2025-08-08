import datetime
import time
import pytest
import jwt
from unittest.mock import patch
import services.shared.j4s_jwt_lib.jwt_processor as jwt_processor


class TestJwtTokenProcessor:
    """Test suite for JwtTokenProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.issuer = "test_issuer"
        self.audience = "test_audience"
        self.secret_key = "test_secret_key_123"
        self.expiry_milli_seconds = 3600
        self.jwt_processor = jwt_processor.JwtTokenProcessor(
            issuer=self.issuer,
            audience=self.audience,
            secret_key=self.secret_key,
            expiry_milli_seconds=self.expiry_milli_seconds
        )
    
    def test_init_with_default_expiry(self):
        """Test initialization with default expiry time."""
        processor = jwt_processor.JwtTokenProcessor(
            issuer="test",
            audience="test", 
            secret_key="test"
        )
        assert processor.issuer == "test"
        assert processor.audience == "test"
        assert processor.secret_key == "test"
        assert processor.expiry_milli_seconds == 3600  # Default value
    
    def test_init_with_custom_expiry(self):
        """Test initialization with custom expiry time."""
        custom_expiry = 7200
        processor = jwt_processor.JwtTokenProcessor(
            issuer=self.issuer,
            audience=self.audience,
            secret_key=self.secret_key,
            expiry_milli_seconds=custom_expiry
        )
        assert processor.expiry_milli_seconds == custom_expiry
    
    def test_generate_token_basic_payload(self):
        """Test token generation with basic payload."""
        payload = {"user_id": 123, "username": "testuser"}
        token = self.jwt_processor.generate_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode the token to verify contents
        decoded = self.jwt_processor.decode_token(token)        
        
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert decoded["iss"] == self.issuer
        assert decoded["aud"] == self.audience
        assert "exp" in decoded
    
    def test_generate_token_empty_payload(self):
        """Test token generation with empty payload."""
        payload = {}
        token = self.jwt_processor.generate_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0

        decoded = self.jwt_processor.decode_token(token)
        
        assert decoded["iss"] == self.issuer
        assert decoded["aud"] == self.audience
        assert "exp" in decoded
    
    def test_generate_token_with_existing_iss_aud(self):
        """Test that issuer and audience are overridden in payload."""
        payload = {
            "user_id": 123,
            "iss": "old_issuer",
            "aud": "old_audience"
        }
        token = self.jwt_processor.generate_token(payload)

        decoded = self.jwt_processor.decode_token(token)
        
        # Should use the processor's issuer and audience, not the ones in payload
        assert decoded["iss"] == self.issuer
        assert decoded["aud"] == self.audience
        assert decoded["user_id"] == 123
    
    def test_generate_token_expiry(self):
        
        self.jwt_processor = jwt_processor.JwtTokenProcessor(
            issuer="ABC",
            audience="PQR",
            secret_key="ljlkjiew7897ew",
            expiry_milli_seconds=10
        )
        payload = {"user_id": 123}
        token = self.jwt_processor.generate_token(payload)
        
        time.sleep(1)

        result = self.jwt_processor.decode_token(token)

        assert "error" in result
        assert result["error"] == "Token has expired"

    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        payload = {"user_id": 123, "username": "testuser"}
        token = self.jwt_processor.generate_token(payload)
        
        decoded = self.jwt_processor.decode_token(token)
        
        assert "error" not in decoded
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert decoded["iss"] == self.issuer
        assert decoded["aud"] == self.audience
    
    def test_decode_token_invalid_signature(self):
        """Test decoding a token with invalid signature."""
        payload = {"user_id": 123}
        # Create token with different secret
        different_processor = jwt_processor.JwtTokenProcessor(
            issuer=self.issuer,
            audience=self.audience,
            secret_key="different_secret"
        )
        token = different_processor.generate_token(payload)
        
        result = self.jwt_processor.decode_token(token)
        
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_decode_token_wrong_audience(self):
        """Test decoding a token with wrong audience."""
        payload = {"user_id": 123}
        # Create token with different audience
        different_processor = jwt_processor.JwtTokenProcessor(
            issuer=self.issuer,
            audience="different_audience",
            secret_key=self.secret_key
        )
        token = different_processor.generate_token(payload)
        
        result = self.jwt_processor.decode_token(token)
        
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_decode_token_wrong_issuer(self):
        """Test decoding a token with wrong issuer."""
        payload = {"user_id": 123}
        # Create token with different issuer
        different_processor = jwt_processor.JwtTokenProcessor(
            issuer="different_issuer",
            audience=self.audience,
            secret_key=self.secret_key
        )
        token = different_processor.generate_token(payload)
        
        result = self.jwt_processor.decode_token(token)
        
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_decode_token_expired(self):
        """Test decoding an expired token."""
        # Create a processor with very short expiry
        short_expiry_processor = jwt_processor.JwtTokenProcessor(
            issuer=self.issuer,
            audience=self.audience,
            secret_key=self.secret_key,
            expiry_milli_seconds=0  # Immediate expiry
        )
        
        payload = {"user_id": 123}
        token = short_expiry_processor.generate_token(payload)
        
        # Wait a moment to ensure expiry
        import time
        time.sleep(0.1)
        
        result = self.jwt_processor.decode_token(token)
        
        assert "error" in result
        assert result["error"] == "Token has expired"
    
    def test_decode_token_malformed(self):
        """Test decoding a malformed token."""
        malformed_token = "not.a.valid.jwt.token"
        
        result = self.jwt_processor.decode_token(malformed_token)
        
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_decode_token_empty_string(self):
        """Test decoding an empty token."""
        result = self.jwt_processor.decode_token("")
        
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_round_trip_token(self):
        """Test generating and then decoding a token (round trip)."""
        original_payload = {
            "user_id": 456,
            "username": "roundtripuser",
            "roles": ["admin", "user"],
            "active": True
        }
        
        # Generate token
        token = self.jwt_processor.generate_token(original_payload.copy())
        
        # Decode token
        decoded_payload = self.jwt_processor.decode_token(token)
        
        # Verify original data is preserved
        assert "error" not in decoded_payload
        assert decoded_payload["user_id"] == original_payload["user_id"]
        assert decoded_payload["username"] == original_payload["username"]
        assert decoded_payload["roles"] == original_payload["roles"]
        assert decoded_payload["active"] == original_payload["active"]
        
        # Verify standard claims are added
        assert decoded_payload["iss"] == self.issuer
        assert decoded_payload["aud"] == self.audience
        assert "exp" in decoded_payload
    
    def test_multiple_processors_different_secrets(self):
        """Test that tokens from different processors can't be decoded by each other."""
        processor1 = jwt_processor.JwtTokenProcessor(
            issuer="issuer1",
            audience="audience1",
            secret_key="secret1"
        )
        
        processor2 = jwt_processor.JwtTokenProcessor(
            issuer="issuer1",
            audience="audience1",
            secret_key="secret2"  # Different secret
        )
        
        payload = {"user_id": 123}
        token1 = processor1.generate_token(payload)
        
        # processor2 should not be able to decode token1
        result = processor2.decode_token(token1)
        assert "error" in result
        assert result["error"] == "Invalid token"
    
    def test_complex_payload_types(self):
        """Test token generation and decoding with complex payload types."""
        complex_payload = {
            "user_id": 789,
            "permissions": ["read", "write", "delete"],
            "metadata": {
                "last_login": "2023-01-01T12:00:00Z",
                "session_count": 5
            },
            "is_admin": False,
            "score": 95.5
        }
        
        token = self.jwt_processor.generate_token(complex_payload.copy())
        decoded = self.jwt_processor.decode_token(token)
        
        assert "error" not in decoded
        assert decoded["user_id"] == 789
        assert decoded["permissions"] == ["read", "write", "delete"]
        assert decoded["metadata"]["last_login"] == "2023-01-01T12:00:00Z"
        assert decoded["metadata"]["session_count"] == 5
        assert decoded["is_admin"] is False
        assert decoded["score"] == 95.5
