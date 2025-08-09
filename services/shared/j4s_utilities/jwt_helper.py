"""JWT Helper module for centralized JWT token management."""
from pathlib import Path
import yaml
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

from services.shared.j4s_utilities.token_models import TokenPayload
from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor


class JwtHelper:
    """
    Centralized JWT helper for token generation and validation.
    
    Features:
    - Configuration loaded from yaml file using pathlib
    - Type-safe token payload handling
    - Consistent error handling across services
    - Single point of configuration management
    """
    
    def __init__(self):
        self._jwt_processor = None
        self._security = HTTPBearer()
        self._load_config()
    
    def _load_config(self):
        """Load JWT configuration using pathlib (Option A)."""
        try:
            # Navigate from current file to services root, then to config
            current_file = Path(__file__)
            services_root = current_file.parent.parent.parent  # services/
            config_path = services_root / "config" / "jwt_config.yml"
            
            if not config_path.exists():
                raise FileNotFoundError(f"JWT config not found at: {config_path}")
            
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            jwt_config = config['jwt']
            self._jwt_processor = JwtTokenProcessor(
                issuer=jwt_config['issuer'],
                audience=jwt_config['audience'],
                secret_key=jwt_config['secret_key'],
                expiry_milli_seconds=jwt_config['expiry_milliseconds']
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to load JWT configuration: {e}")
    
    def generate_token(self, token_payload: TokenPayload) -> str:
        """
        Generate JWT token from TokenPayload.
        
        Args:
            token_payload: TokenPayload instance with user data
            
        Returns:
            str: JWT token string
        """
        payload_dict = token_payload.to_dict()
        return self._jwt_processor.generate_token(payload_dict)
    
    def verify_token(self, authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> TokenPayload:
        """
        Verify JWT token and return TokenPayload.
        
        This function is designed to be used as a FastAPI dependency.
        
        Args:
            authorization: HTTP Bearer credentials from FastAPI
            
        Returns:
            TokenPayload: Validated token payload
            
        Raises:
            HTTPException: If token is invalid or malformed
        """
        try:
            token = authorization.credentials
            payload = self._jwt_processor.decode_token(token)
            
            # Check if JWT processor returned an error
            if "error" in payload:
                raise HTTPException(
                    status_code=401,
                    detail=payload["error"],
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Convert to TokenPayload with validation
            try:
                return TokenPayload(**payload)
            except ValidationError as e:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid token payload structure: {str(e)}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Token validation failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @property
    def security(self) -> HTTPBearer:
        """Get the HTTPBearer security instance for dependency injection."""
        return self._security


# Global instance for use across the application
jwt_helper = JwtHelper()
