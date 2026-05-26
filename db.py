## backend/db.py

from multiprocessing import connection
import sqlite3
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # rows are like dicts
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS torrents (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT,
            magnet       TEXT NOT NULL,
            status       TEXT NOT NULL DEFAULT 'queued',
            progress     REAL NOT NULL DEFAULT 0.0,
            download_rate INTEGER NOT NULL DEFAULT 0,
            upload_rate   INTEGER NOT NULL DEFAULT 0,
            size         INTEGER,
            save_path    TEXT,
            error        TEXT,
            added_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            finished_at  DATETIME
        );
    """)
    conn.commit()
    conn.close()