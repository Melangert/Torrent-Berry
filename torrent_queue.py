import sqlite3
from db import get_connection

def add_torrent(magnet: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO torrents (magnet, status)
        VALUES (?, 'queued')
    """, (magnet,))

    conn.commit()
    torrent_id = cursor.lastrowid
    conn.close()
    return torrent_id

def get_next_queued() -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM torrents
        WHERE status = 'queued'
        ORDER BY added_at ASC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_torrent(torrent_id: int, **kwargs):
    if not kwargs:
        return

    fields = ", ".join(f"{key} = ?" for key in kwargs.keys())
    values = list(kwargs.values())
    values.append(torrent_id)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE torrents
        SET {fields}
        WHERE id = ?
    """, values)

    conn.commit()
    conn.close()

def get_all_torrents() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM torrents ORDER BY added_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_torrent(torrent_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM torrents WHERE id = ?", (torrent_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

