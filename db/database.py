# db/database.py

import sqlite3
from typing import Optional
import datetime
import os

DEFAULT_DB_PATH = "storage/core_units.db"

def create_database(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Creates an SQLite database with support for indexes and meta tables.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)

    try:
        conn.enable_load_extension(True)
        conn.execute("SELECT json('[]')")
    except sqlite3.OperationalError:
        print("⚠️ SQLite does not support JSON1 – some queries may not work.")

    cursor = conn.cursor()

    # Core units table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_units (
            id TEXT PRIMARY KEY,
            stem TEXT,
            concept TEXT,
            pos TEXT,
            main_pos TEXT,
            definition_set TEXT,
            related TEXT,
            source TEXT,
            last_updated TEXT
        )
    """)

    # Meta table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stem ON core_units(stem);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_concept ON core_units(concept);")

    conn.commit()
    return conn

def update_meta(conn: sqlite3.Connection, key: str, value: str):
    """
    Updates or creates a value in the meta table.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO meta (key, value)
        VALUES (?, ?)
    """, (key, value))
    conn.commit()

def initialize_meta(conn: sqlite3.Connection):
    """
    Initializes basic meta data such as creation time and word count.
    """
    update_meta(conn, "build_timestamp", datetime.datetime.utcnow().isoformat())
    update_meta(conn, "system_version", "1.0.0")
