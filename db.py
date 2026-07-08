import sqlite3
import json
import uuid
from datetime import datetime

DB_PATH = "resume_agent.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            public_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            ats_score INTEGER NOT NULL,
            analysis_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- Users ----------

def create_user(email: str, password_hash: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
        (email, password_hash, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- Resumes ----------

def save_resume(user_id: int, filename: str, analysis: dict) -> str:
    public_id = uuid.uuid4().hex[:10]
    conn = get_conn()
    conn.execute(
        """INSERT INTO resumes (user_id, public_id, filename, ats_score, analysis_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, public_id, filename, analysis.get("ats_score", 0),
         json.dumps(analysis), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return public_id


def get_history(user_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_resume_by_public_id(public_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM resumes WHERE public_id = ?", (public_id,)).fetchone()
    conn.close()
    return dict(row) if row else None