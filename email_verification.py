import hashlib
import hmac
import os
import secrets
import smtplib
import sqlite3
import time
from email.message import EmailMessage
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "verification.db"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CODE_EXPIRY_SECONDS = 600
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5
PBKDF2_ITERATIONS = 200_000


def _connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verification_codes (
            email TEXT PRIMARY KEY COLLATE NOCASE,
            code_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0
        )
    """)
    return conn


def _hash_code(code, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", code.encode("utf-8"), salt, PBKDF2_ITERATIONS
    ).hex()


def _send_email(recipient, code):
    sender = os.getenv("SAY_EMAIL_ADDRESS")
    app_password = os.getenv("SAY_EMAIL_APP_PASSWORD")

    if not sender or not app_password:
        raise RuntimeError(
            "Email is not configured. Set SAY_EMAIL_ADDRESS and "
            "SAY_EMAIL_APP_PASSWORD in the VS Code terminal."
        )

    message = EmailMessage()
    message["Subject"] = "Your Say verification code"
    message["From"] = f"Say <{sender}>"
    message["To"] = recipient
    message.set_content(
        f"Welcome to Say!\n\nYour verification code is {code}.\n"
        "It expires in 10 minutes. If you did not request this, "
        "you can ignore this email.\n\nThe Say team"
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, app_password)
        server.send_message(message)


def send_verification_code(email):
    email = email.strip().lower()
    now = time.time()

    with _connection() as conn:
        previous = conn.execute(
            "SELECT created_at FROM verification_codes WHERE email = ?",
            (email,)
        ).fetchone()
        if previous and now - previous[0] < RESEND_COOLDOWN_SECONDS:
            wait = int(RESEND_COOLDOWN_SECONDS - (now - previous[0])) + 1
            raise ValueError(f"Please wait {wait} seconds before requesting another code.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    salt = secrets.token_bytes(16)
    code_hash = _hash_code(code, salt)

    # Send first; only replace the previous code if delivery succeeds.
    _send_email(email, code)

    with _connection() as conn:
        conn.execute("""
            INSERT INTO verification_codes
                (email, code_hash, salt, created_at, expires_at, attempts)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(email) DO UPDATE SET
                code_hash = excluded.code_hash,
                salt = excluded.salt,
                created_at = excluded.created_at,
                expires_at = excluded.expires_at,
                attempts = 0
        """, (email, code_hash, salt.hex(), now, now + CODE_EXPIRY_SECONDS))


def verify_verification_code(email, entered_code):
    email = email.strip().lower()
    entered_code = entered_code.strip()

    if len(entered_code) != 6 or not entered_code.isdigit():
        return False

    with _connection() as conn:
        row = conn.execute("""
            SELECT code_hash, salt, expires_at, attempts
            FROM verification_codes WHERE email = ?
        """, (email,)).fetchone()

        if not row:
            return False

        stored_hash, salt_hex, expires_at, attempts = row

        if time.time() > expires_at or attempts >= MAX_ATTEMPTS:
            conn.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
            return False

        entered_hash = _hash_code(entered_code, bytes.fromhex(salt_hex))
        if not hmac.compare_digest(entered_hash, stored_hash):
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                conn.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
            else:
                conn.execute(
                    "UPDATE verification_codes SET attempts = ? WHERE email = ?",
                    (attempts, email)
                )
            return False

        conn.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        return True
