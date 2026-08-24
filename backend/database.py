import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent / "event.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            members TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            problem TEXT NOT NULL,
            description TEXT NOT NULL,
            webhook_url TEXT NOT NULL,
            tools TEXT,
            workflow_json TEXT,
            status TEXT DEFAULT 'submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(team_id) REFERENCES teams(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            functionality REAL DEFAULT 0,
            quality REAL DEFAULT 0,
            robustness REAL DEFAULT 0,
            final_score REAL DEFAULT 0,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(submission_id) REFERENCES submissions(id)
        )
    """)

    conn.commit()
    conn.close()


def create_team(team_name, username, password, members):
    conn = get_db()

    existing = conn.execute(
        "SELECT id FROM teams WHERE username = ?",
        (username,)
    ).fetchone()

    if existing:
        conn.close()
        return False

    conn.execute("""
        INSERT INTO teams (
            team_name,
            username,
            password_hash,
            members
        )
        VALUES (?, ?, ?, ?)
    """, (
        team_name,
        username,
        generate_password_hash(password),
        json.dumps(members)
    ))

    conn.commit()
    conn.close()

    return True
