import sqlite3
from datetime import datetime
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitor_pulse.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create competitors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create scrapes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrapes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            scrape_type TEXT NOT NULL, -- 'pricing', 'careers', 'homepage', 'news'
            raw_content TEXT,
            extracted_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
        )
    """)
    
    # Create analysis_reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            battlecard_md TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def add_competitor(name: str, domain: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO competitors (name, domain, updated_at) VALUES (?, ?, ?)",
            (name, domain, datetime.now().isoformat())
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Competitor already exists, update updated_at and get ID
        cursor.execute("SELECT id FROM competitors WHERE domain = ?", (domain,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE competitors SET name = ?, updated_at = ? WHERE id = ?",
                (name, datetime.now().isoformat(), row['id'])
            )
            conn.commit()
            return row['id']
    finally:
        conn.close()

def get_all_competitors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitors ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_competitor(competitor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitors WHERE id = ?", (competitor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_scrape(competitor_id: int, url: str, scrape_type: str, raw_content: str, extracted_text: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO scrapes (competitor_id, url, scrape_type, raw_content, extracted_text, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (competitor_id, url, scrape_type, raw_content, extracted_text, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_latest_scrape(competitor_id: int, scrape_type: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM scrapes WHERE competitor_id = ? AND scrape_type = ? ORDER BY created_at DESC LIMIT 1",
        (competitor_id, scrape_type)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_analysis(competitor_id: int, title: str, summary: str, battlecard_md: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO analysis_reports (competitor_id, title, summary, battlecard_md, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (competitor_id, title, summary, battlecard_md, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_latest_analysis(competitor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analysis_reports WHERE competitor_id = ? ORDER BY created_at DESC LIMIT 1",
        (competitor_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_analysis_history(competitor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analysis_reports WHERE competitor_id = ? ORDER BY created_at DESC",
        (competitor_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
