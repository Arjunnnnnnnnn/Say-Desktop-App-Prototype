import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "say_local.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                say_id TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT NOT NULL DEFAULT 'light'
                    CHECK(theme IN ('light', 'dark')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chat_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'accepted', 'declined')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK(sender_id <> receiver_id),
                UNIQUE(sender_id, receiver_id),
                FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_one INTEGER NOT NULL,
                user_two INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK(user_one < user_two),
                UNIQUE(user_one, user_two),
                FOREIGN KEY(user_one) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(user_two) REFERENCES users(id) ON DELETE CASCADE
            )
        """)


def create_user(email, say_id, password_hash, password_salt):
    email = email.strip().lower()
    say_id = say_id.strip().lstrip("@").lower()
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO users (email, say_id, password_hash, password_salt)
            VALUES (?, ?, ?, ?)
        """, (email, say_id, password_hash, password_salt))
        user_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO user_preferences (user_id, theme) VALUES (?, 'light')",
            (user_id,)
        )
        return user_id


def get_user_by_email(email):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_say_id(say_id):
    normalized = say_id.strip().lstrip("@").lower()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, say_id FROM users WHERE say_id = ?", (normalized,)
        ).fetchone()
        return dict(row) if row else None


def search_users(say_id, current_user_id):
    normalized = say_id.strip().lstrip("@").lower()
    if not normalized:
        return []
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, say_id
            FROM users
            WHERE say_id LIKE ? AND id <> ?
            ORDER BY say_id
            LIMIT 20
        """, (f"%{normalized}%", current_user_id)).fetchall()
        return [dict(row) for row in rows]


def get_theme(user_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT theme FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["theme"] if row else "light"


def save_theme(user_id, theme):
    if theme not in ("light", "dark"):
        raise ValueError("Invalid theme.")
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO user_preferences (user_id, theme)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET theme = excluded.theme
        """, (user_id, theme))


def send_chat_request(sender_id, receiver_id):
    if sender_id == receiver_id:
        raise ValueError("You cannot send a chat request to yourself.")

    with get_connection() as connection:
        receiver = connection.execute(
            "SELECT id FROM users WHERE id = ?", (receiver_id,)
        ).fetchone()
        if not receiver:
            raise ValueError("That Say ID could not be found.")

        existing = connection.execute("""
            SELECT id, status FROM chat_requests
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
        """, (sender_id, receiver_id, receiver_id, sender_id)).fetchone()

        if existing:
            if existing["status"] == "accepted":
                raise ValueError("You are already connected.")
            if existing["status"] == "pending":
                raise ValueError("A request between these users is already pending.")
            # A declined request can be re-sent by the original sender.
            connection.execute("""
                UPDATE chat_requests
                SET sender_id = ?, receiver_id = ?, status = 'pending',
                    created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (sender_id, receiver_id, existing["id"]))
            return

        connection.execute("""
            INSERT INTO chat_requests (sender_id, receiver_id)
            VALUES (?, ?)
        """, (sender_id, receiver_id))


def get_incoming_requests(user_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT cr.id, cr.sender_id, u.say_id, cr.created_at
            FROM chat_requests cr
            JOIN users u ON u.id = cr.sender_id
            WHERE cr.receiver_id = ? AND cr.status = 'pending'
            ORDER BY cr.created_at DESC
        """, (user_id,)).fetchall()
        return [dict(row) for row in rows]


def get_outgoing_requests(user_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT cr.id, cr.receiver_id, u.say_id, cr.created_at
            FROM chat_requests cr
            JOIN users u ON u.id = cr.receiver_id
            WHERE cr.sender_id = ? AND cr.status = 'pending'
            ORDER BY cr.created_at DESC
        """, (user_id,)).fetchall()
        return [dict(row) for row in rows]


def respond_to_chat_request(request_id, user_id, accept):
    with get_connection() as connection:
        request = connection.execute("""
            SELECT sender_id, receiver_id, status
            FROM chat_requests
            WHERE id = ? AND receiver_id = ?
        """, (request_id, user_id)).fetchone()

        if not request or request["status"] != "pending":
            raise ValueError("This request is no longer available.")

        new_status = "accepted" if accept else "declined"
        connection.execute("""
            UPDATE chat_requests
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, request_id))

        if accept:
            one, two = sorted((request["sender_id"], request["receiver_id"]))
            connection.execute("""
                INSERT OR IGNORE INTO conversations (user_one, user_two)
                VALUES (?, ?)
            """, (one, two))


def get_conversations(user_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT c.id AS conversation_id,
                   CASE WHEN c.user_one = ? THEN u2.id ELSE u1.id END AS other_user_id,
                   CASE WHEN c.user_one = ? THEN u2.say_id ELSE u1.say_id END AS other_say_id
            FROM conversations c
            JOIN users u1 ON u1.id = c.user_one
            JOIN users u2 ON u2.id = c.user_two
            WHERE c.user_one = ? OR c.user_two = ?
            ORDER BY c.created_at DESC
        """, (user_id, user_id, user_id, user_id)).fetchall()
        return [dict(row) for row in rows]
