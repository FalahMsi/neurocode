# db/database.py

import sqlite3
from typing import Optional
import datetime
import os

DEFAULT_DB_PATH = "storage/core_units.db"

def create_database(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    ينشئ قاعدة بيانات SQLite مع دعم الفهارس وجداول meta.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)

    try:
        conn.enable_load_extension(True)
        conn.execute("SELECT json('[]')")
    except sqlite3.OperationalError:
        print("⚠️ SQLite لا يدعم JSON1 – بعض الاستعلامات قد لا تعمل.")

    cursor = conn.cursor()

    # جدول اللبنات
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

    # جدول meta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # فهارس
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stem ON core_units(stem);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_concept ON core_units(concept);")

    conn.commit()
    return conn

def update_meta(conn: sqlite3.Connection, key: str, value: str):
    """
    يحدث أو ينشئ قيمة داخل جدول meta.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO meta (key, value)
        VALUES (?, ?)
    """, (key, value))
    conn.commit()

def initialize_meta(conn: sqlite3.Connection):
    """
    تهيئة بيانات meta الأساسية مثل وقت الإنشاء وعدد الكلمات.
    """
    update_meta(conn, "build_timestamp", datetime.datetime.utcnow().isoformat())
    update_meta(conn, "system_version", "1.0.0")
