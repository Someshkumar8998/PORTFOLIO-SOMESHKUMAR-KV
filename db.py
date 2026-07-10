"""
Plain sqlite3 (Python standard library) data layer.
This replaces Django's ORM/models.py entirely — no framework involved.

Tables mirror the original Django models:
  skills, services, projects, experience, certifications, contact_messages

If a table is empty, views.py falls back to the defaults in data.py,
exactly like the original Django views did.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icon TEXT DEFAULT '',
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subtitle TEXT DEFAULT '',
    project_type TEXT DEFAULT '',
    description TEXT NOT NULL,
    image TEXT DEFAULT '',
    video TEXT DEFAULT '',
    link TEXT DEFAULT '',
    tech_stack TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT DEFAULT '',
    period_start TEXT DEFAULT '',
    period_end TEXT DEFAULT 'Present',
    description TEXT DEFAULT '',
    bullets TEXT DEFAULT '',
    tech_stack TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT DEFAULT '',
    message TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def _rows(table, order_by="sort_order, id"):
    with get_conn() as conn:
        cur = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}")
        return [dict(r) for r in cur.fetchall()]


def get_skills():
    return _rows("skills")


def get_services():
    return _rows("services")


def get_projects():
    rows = _rows("projects")
    for r in rows:
        r["tech_list"] = [t.strip() for t in (r.get("tech_stack") or "").split(",") if t.strip()]
        r["video"] = r.get("video") or None
    return rows


def get_experience():
    rows = _rows("experience")
    for r in rows:
        r["bullet_list"] = [b.strip() for b in (r.get("bullets") or "").splitlines() if b.strip()]
        r["tech_list"] = [t.strip() for t in (r.get("tech_stack") or "").split(",") if t.strip()]
    return rows


def get_certifications():
    return _rows("certifications")


def save_contact_message(name, email, subject, message):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
            (name, email, subject, message),
        )
        return cur.lastrowid
