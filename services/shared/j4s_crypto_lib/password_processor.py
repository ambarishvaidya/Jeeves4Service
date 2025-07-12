import hashlib
import secrets

def generate_salt() -> bytes:
    return secrets.token_hex(16).encode()


def generate_hash(password: str) -> tuple[bytes, bytes]:
    salt = generate_salt()
    print(f"Generated Salt: {type(salt)}, {salt}")
    encoded_password = password.encode()
    combined = encoded_password + salt
    return (hashlib.sha256(combined).digest(), salt)
    

def verify_password(stored_hash: bytes, password: str, salt: bytes) -> bool:
    encoded_password = password.encode()
    combined = encoded_password + salt
    hashed_password = hashlib.sha256(combined).digest()
    return hashed_password == stored_hash


def __repr__() -> str:
    return "Password Processor Module: Provides functions to generate and verify password."


def __str__() -> str:
    return "This module contains functions to securely generate and verify password hashes using SHA-256 and a random salt."

if __name__ == "__main__":
    password = "my_secure_password"
    hashed_password, salt = generate_hash(password)
    print(f"Hashed Password: {hashed_password}")
    # Example usage of verify_password
    is_valid = verify_password(hashed_password, password, salt)
    print(f"Is the password valid? {is_valid}")

    ...