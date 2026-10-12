"""
SQLite Database interface for HealthAI Authentication, User Management,
Audit Logging, and Assessment Statistics.
Maintains data integrity, parameterized queries, and strict role-based access.
"""

import sqlite3
import os
import json
import secrets
import hashlib
import bcrypt
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "disease_prediction.db")


def get_db_connection():
    """Returns an active SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str) -> str:
    """Hashes a raw password string using bcrypt with 12 salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a raw password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def hash_token(token: str) -> str:
    """Computes a SHA-256 hash of a token for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def init_db():
    """Initializes database tables, runs required schema migrations, and seeds default admin."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # 2. Server-side Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            csrf_token TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 3. Login Attempts (Rate Limiting & Brute Force Defense)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,
            attempt_time TEXT NOT NULL,
            success INTEGER NOT NULL DEFAULT 0
        )
    """)

    # 4. Password Resets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 5. Assessment History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symptoms_count INTEGER NOT NULL,
            symptoms_list TEXT NOT NULL,
            primary_prediction TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            emergency_flag INTEGER NOT NULL DEFAULT 0,
            specialist_referred TEXT,
            user_id INTEGER DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    # Check for schema migration: ensure user_id column exists on assessment_history
    cursor.execute("PRAGMA table_info(assessment_history)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE assessment_history ADD COLUMN user_id INTEGER DEFAULT NULL;")

    conn.commit()

    # Seed initial default administrator if none exists
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin_exists = cursor.fetchone()
    if not admin_exists:
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@healthai.local").strip().lower()
        admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@HealthAI2026!")
        admin_name = os.environ.get("ADMIN_NAME", "System Administrator").strip()

        # Check if email is already taken
        cursor.execute("SELECT id FROM users WHERE email = ? COLLATE NOCASE", (admin_email,))
        existing_user = cursor.fetchone()
        now = datetime.now(timezone.utc).isoformat()
        if existing_user:
            cursor.execute("UPDATE users SET role = 'admin', updated_at = ? WHERE id = ?", (now, existing_user["id"]))
        else:
            pwd_hash = hash_password(admin_password)
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (?, ?, ?, 'admin', 1, ?, ?)
            """, (admin_name, admin_email, pwd_hash, now, now))
        conn.commit()

    conn.close()


# ============================================================================
# User Operations
# ============================================================================

def create_user(full_name: str, email: str, password: str, role: str = "user") -> dict:
    """Registers a new user account with hashed password and parameterized query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    clean_email = email.strip().lower()
    clean_name = full_name.strip()
    pwd_hash = hash_password(password)

    # Force role to 'user' unless explicitly specified by internal processes
    assigned_role = 'admin' if role == 'admin' else 'user'

    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """, (clean_name, clean_email, pwd_hash, assigned_role, now, now))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "full_name": clean_name,
        "email": clean_email,
        "role": assigned_role,
        "created_at": now
    }


def get_user_by_email(email: str):
    """Fetches user record by email (case-insensitive)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = email.strip().lower()
    cursor.execute("""
        SELECT id, full_name, email, password_hash, role, is_active, created_at, updated_at
        FROM users WHERE email = ? COLLATE NOCASE
    """, (clean_email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int):
    """Fetches user record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, password_hash, role, is_active, created_at, updated_at
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def update_user_profile(user_id: int, full_name: str = None, email: str = None, password: str = None) -> dict:
    """Updates user full name, email, and/or password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    updates = ["updated_at = ?"]
    params = [now]

    if full_name:
        updates.append("full_name = ?")
        params.append(full_name.strip())
    if email:
        updates.append("email = ?")
        params.append(email.strip().lower())
    if password:
        updates.append("password_hash = ?")
        params.append(hash_password(password))

    params.append(user_id)
    sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, tuple(params))
    conn.commit()
    conn.close()

    return get_user_by_id(user_id)


def delete_user_account(user_id: int):
    """Permanently deletes user account, associated sessions, resets, and personal assessment history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete personal assessment history
    cursor.execute("DELETE FROM assessment_history WHERE user_id = ?", (user_id,))
    # Delete sessions
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    # Delete password resets
    cursor.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))
    # Delete user record
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()


def list_all_users():
    """Administrator query: retrieves all registered users without exposing password hashes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.full_name, u.email, u.role, u.is_active, u.created_at, u.updated_at,
               COUNT(a.id) as assessments_count
        FROM users u
        LEFT JOIN assessment_history a ON a.user_id = u.id
        GROUP BY u.id
        ORDER BY u.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_status(user_id: int, is_active: bool = None, role: str = None):
    """Administrator operation: updates account active state or role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    updates = ["updated_at = ?"]
    params = [now]

    if is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if is_active else 0)
    if role in ("user", "admin"):
        updates.append("role = ?")
        params.append(role)

    params.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", tuple(params))
    conn.commit()
    conn.close()


# ============================================================================
# Session Management
# ============================================================================

def create_session(user_id: int, ip_address: str = None, user_agent: str = None, duration_days: int = 7) -> dict:
    """Generates a cryptographically secure random session and CSRF token."""
    session_id = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(days=duration_days)).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, csrf_token, created_at, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, csrf_token, now.isoformat(), expires_at, ip_address, user_agent))
    conn.commit()
    conn.close()

    return {
        "session_id": session_id,
        "csrf_token": csrf_token,
        "expires_at": expires_at
    }


def get_session(session_id: str):
    """Validates session token and returns active session row with user data."""
    if not session_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.session_id, s.user_id, s.csrf_token, s.expires_at,
               u.id as uid, u.full_name, u.email, u.role, u.is_active
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_id = ?
    """, (session_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    # Check expiration
    expires_at = datetime.fromisoformat(row["expires_at"])
    now = datetime.now(timezone.utc)
    if now > expires_at:
        # Delete expired session
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return None

    conn.close()
    return {
        "session_id": row["session_id"],
        "user_id": row["user_id"],
        "csrf_token": row["csrf_token"],
        "expires_at": row["expires_at"],
        "user": {
            "id": row["uid"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": row["role"],
            "is_active": bool(row["is_active"])
        }
    }


def delete_session(session_id: str):
    """Invalidates and deletes a session upon logout."""
    if not session_id:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def delete_all_user_sessions(user_id: int):
    """Invalidates all active sessions for a user (e.g. after password reset)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ============================================================================
# Rate Limiting & Brute Force Defense
# ============================================================================

def record_login_attempt(identifier: str, success: bool):
    """Logs a login attempt for rate limiting calculations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO login_attempts (identifier, attempt_time, success)
        VALUES (?, ?, ?)
    """, (identifier.lower(), now, 1 if success else 0))
    conn.commit()
    conn.close()


def is_rate_limited(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Checks if an IP or email identifier exceeded failed attempts within window."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE identifier = ? AND success = 0 AND attempt_time >= ?
    """, (identifier.lower(), cutoff))
    count = cursor.fetchone()[0]
    conn.close()
    return count >= max_attempts


def clear_failed_attempts(identifier: str):
    """Clears failed attempts upon successful login."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM login_attempts WHERE identifier = ?", (identifier.lower(),))
    conn.commit()
    conn.close()


# ============================================================================
# Password Reset Tokens
# ============================================================================

def create_password_reset_token(user_id: int, duration_minutes: int = 60) -> str:
    """Generates a secure password reset token and saves its SHA-256 hash."""
    plain_token = secrets.token_urlsafe(32)
    token_hashed = hash_token(plain_token)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(minutes=duration_minutes)).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO password_resets (user_id, token_hash, expires_at, used, created_at)
        VALUES (?, ?, ?, 0, ?)
    """, (user_id, token_hashed, expires_at, now.isoformat()))
    conn.commit()
    conn.close()

    return plain_token


def verify_password_reset_token(token: str):
    """Verifies a password reset token; returns user record if valid and unexpired."""
    if not token:
        return None
    token_hashed = hash_token(token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.user_id, r.expires_at, r.used, u.email, u.full_name
        FROM password_resets r
        JOIN users u ON r.user_id = u.id
        WHERE r.token_hash = ? AND r.used = 0
    """, (token_hashed,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return None

    return dict(row)


def consume_password_reset_token(token: str, new_password: str) -> bool:
    """Consumes reset token, updates password hash, and invalidates all existing sessions."""
    reset_data = verify_password_reset_token(token)
    if not reset_data:
        return False

    user_id = reset_data["user_id"]
    token_hashed = hash_token(token)
    now = datetime.now(timezone.utc).isoformat()
    new_hash = hash_password(new_password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE password_resets SET used = 1 WHERE token_hash = ?", (token_hashed,))
    cursor.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now, user_id))
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return True


# ============================================================================
# Assessment Logging & Privacy History
# ============================================================================

def log_assessment(symptoms, primary_prediction, confidence, emergency_flag, specialist, user_id=None):
    """Log a prediction event linked optionally to user_id while preserving privacy-safe structure."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_history (
            timestamp, symptoms_count, symptoms_list,
            primary_prediction, confidence_score, emergency_flag, specialist_referred, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        len(symptoms),
        json.dumps(symptoms),
        primary_prediction,
        round(confidence, 4),
        1 if emergency_flag else 0,
        specialist,
        user_id
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_history(limit=50, user_id=None, view_all=False):
    """
    Retrieve assessment history.
    - If user_id is provided and not view_all: returns only the user's assessments.
    - If view_all is True: returns system-wide records (admin audit view).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id is not None and not view_all:
        cursor.execute("""
            SELECT id, timestamp, symptoms_count, symptoms_list,
                   primary_prediction, confidence_score, emergency_flag, specialist_referred, user_id
            FROM assessment_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
            SELECT id, timestamp, symptoms_count, symptoms_list,
                   primary_prediction, confidence_score, emergency_flag, specialist_referred, user_id
            FROM assessment_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "symptoms_count": r["symptoms_count"],
            "symptoms": json.loads(r["symptoms_list"]),
            "primary_prediction": r["primary_prediction"],
            "confidence_score": r["confidence_score"],
            "emergency_flag": bool(r["emergency_flag"]),
            "specialist_referred": r["specialist_referred"],
            "user_id": r["user_id"]
        })
    return results


def get_assessment_stats():
    """Retrieve summary counts and frequencies."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM assessment_history")
    total_assessments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE emergency_flag = 1")
    total_emergencies = cursor.fetchone()[0]

    cursor.execute("""
        SELECT primary_prediction, COUNT(*) as count
        FROM assessment_history
        GROUP BY primary_prediction
        ORDER BY count DESC
        LIMIT 5
    """)
    top_conditions = [{"disease": r[0], "count": r[1]} for r in cursor.fetchall()]

    conn.close()
    return {
        "total_assessments": total_assessments,
        "total_emergencies": total_emergencies,
        "top_conditions": top_conditions
    }


def clear_history(user_id=None, is_admin=False):
    """
    Clear assessment records.
    - If user_id is provided and not admin: clears only that user's assessments.
    - If is_admin is True and user_id is None: clears all assessment records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if is_admin and user_id is None:
        cursor.execute("DELETE FROM assessment_history")
    elif user_id is not None:
        cursor.execute("DELETE FROM assessment_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
