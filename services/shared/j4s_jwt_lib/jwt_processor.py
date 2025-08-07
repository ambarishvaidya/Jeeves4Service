from  datetime import datetime, timedelta, timezone
import jwt


class JwtTokenProcessor:

    def __init__(self, issuer: str, audience: str, secret_key: str, expiry_milli_seconds: int =  3600000):
        self.issuer = issuer
        self.audience = audience
        self.secret_key = secret_key
        self.expiry_milli_seconds = expiry_milli_seconds

    def generate_token(self, payload: dict) -> str:
        payload['iss'] = self.issuer
        payload['aud'] = self.audience
        payload['exp'] = datetime.now(timezone.utc) + timedelta(milliseconds=self.expiry_milli_seconds)

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token        

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=['HS256'], 
                audience=self.audience,
                issuer=self.issuer
                )
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}