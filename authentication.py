import hashlib
import hmac
import re
import secrets

PBKDF2_ITERATIONS = 600_000


def normalize_say_id(say_id):
    return say_id.strip().lstrip("@").lower()


def validate_registration(email, say_id, password):
    email = email.strip().lower()
    say_id = normalize_say_id(say_id)

    if not re.fullmatch(r"[A-Za-z0-9._%+-]+@(gmail\.com|googlemail\.com)", email):
        return "Please enter a valid Gmail address."

    if not re.fullmatch(r"[a-z0-9_]{3,20}", say_id):
        return "Say ID must be 3–20 characters and use only letters, numbers, or underscores."

    if len(password) < 10:
        return "Password must contain at least 10 characters."

    if len(password) > 128:
        return "Password is too long."

    return None


def hash_password(password):
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return password_hash.hex(), salt.hex()


def verify_password(password, stored_hash, stored_salt):
    try:
        salt = bytes.fromhex(stored_salt)
        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
        ).hex()
        return hmac.compare_digest(calculated_hash, stored_hash)
    except (ValueError, TypeError):
        return False
