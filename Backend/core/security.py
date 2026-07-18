"""Password and session-token hashing utilities."""

import base64
import binascii
import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    """Return a salted scrypt password hash suitable for database storage."""
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
    )
    return "scrypt$%s$%s" % (
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(derived_key).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Hash a login password with the stored salt and compare safely."""
    try:
        algorithm, encoded_salt, encoded_hash = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.b64decode(encoded_salt, validate=True)
        expected_hash = base64.b64decode(encoded_hash, validate=True)
        candidate_hash = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
        )
    except (AttributeError, ValueError, binascii.Error):
        return False
    return hmac.compare_digest(candidate_hash, expected_hash)


def hash_session_token(token: str) -> str:
    """Store only a one-way hash of each random bearer token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
