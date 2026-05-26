import threading
import time
import shutil
import libtorrent as lt # type: ignore
from config import (
    DOWNLOAD_DIR, INCOMPLETE_DIR,
    LT_DOWNLOAD_LIMIT, LT_UPLOAD_LIMIT,
    LT_MAX_CONNECTIONS, LT_MAX_UPLOADS,
    LT_LISTEN_PORT, POLL_INTERVAL
)
from torrent_queue import get_next_queued, update_torrent, get_torrent
from db import get_connection

SEED_RATIO_LIMIT = 2.0

def make_session() -> lt.session:
    session = lt.session()
    session.listen_on(LT_LISTEN_PORT, LT_LISTEN_PORT + 10)
    settings = {
        "active_downloads": 1,
        "active_seeds": 4,
        "max_out_request_queue": 10,
        "connections_limit": LT_MAX_CONNECTIONS,
        "upload_rate_limit": LT_UPLOAD_LIMIT,
        "download_rate_limit": LT_DOWNLOAD_LIMIT,
    }
    session.apply_settings(settings)
    return session


def add_torrent_to_session(session: lt.session, torrent: dict) -> lt.torrent_handle:
    params = {
        "save_path": str(INCOMPLETE_DIR),
        "storage_mode": lt.storage_mode_t.storage_mode_sparse,
    }
    magnet = torrent["magnet"]
    if magnet.startswith("magnet:"):
        handle = lt.add_magnet_uri(session, magnet, params)
    else:
        info = lt.torrent_info(magnet)
        params["ti"] = info
        handle = session.add_torrent(params)
    return handle


def download(session: lt.session, torrent: dict):
    torrent_id = torrent["id"]
    update_torrent(torrent_id, status="downloading")
    handle = add_torrent_to_session(session, torrent)

    print(f"[{torrent_id}] Waiting for metadata...")
    while not handle.has_metadata():
        time.sleep(1)

    update_torrent(torrent_id, name=handle.name(), size=handle.status().total_wanted)

    # download loop
    while True:
        s = handle.status()
        progress = round(s.progress * 100, 2)
        update_torrent(
            torrent_id,
            progress=progress,
            download_rate=s.download_rate,
            upload_rate=s.upload_rate,
        )

        if s.state == lt.torrent_status.seeding:
            break

        if s.state == lt.torrent_status.error:
            update_torrent(torrent_id, status="error", error=str(s.error))
            session.remove_torrent(handle)
            return

        current = get_torrent(torrent_id)
        if current["status"] == "paused":
            handle.pause()
            while True:
                current = get_torrent(torrent_id)
                if current["status"] == "queued":
                    handle.resume()
                    break
                time.sleep(POLL_INTERVAL)

        time.sleep(POLL_INTERVAL)

    # move finished files to DOWNLOAD_DIR
    finished_path = DOWNLOAD_DIR / handle.name()
    shutil.move(str(INCOMPLETE_DIR / handle.name()), str(finished_path))
    update_torrent(torrent_id, status="seeding", progress=100.0, save_path=str(finished_path))
    print(f"[{torrent_id}] Download complete, seeding until ratio {SEED_RATIO_LIMIT}")

    # seed loop
    while True:
        s = handle.status()
        update_torrent(torrent_id, upload_rate=s.upload_rate)

        if s.state == lt.torrent_status.error:
            update_torrent(torrent_id, status="error", error=str(s.error))
            session.remove_torrent(handle)
            return

        current = get_torrent(torrent_id)
        if current["status"] == "paused":
            handle.pause()
            while True:
                current = get_torrent(torrent_id)
                if current["status"] == "queued":
                    handle.resume()
                    break
                time.sleep(POLL_INTERVAL)

        ratio = s.all_time_upload / s.all_time_download if s.all_time_download > 0 else 0
        if ratio >= SEED_RATIO_LIMIT:
            break

        time.sleep(POLL_INTERVAL)

    session.remove_torrent(handle)
    update_torrent(torrent_id, status="done", upload_rate=0)
    print(f"[{torrent_id}] Seeding complete, ratio {SEED_RATIO_LIMIT} reached")


def recover_interrupted(session: lt.session):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE torrents SET status = 'queued', progress = 0.0
        WHERE status = 'downloading'
    """)
    conn.commit()
    conn.close()
    print("Recovered interrupted downloads")

def run():
    session = make_session()
    recover_interrupted(session)
    print("Torberry downloader started")

    while True:
        torrent = get_next_queued()
        if torrent:
            try:
                t = threading.Thread(target=download, args=(session, torrent), daemon=True)
                t.start()
            except Exception as e:
                print(f"Error: {e}")
                update_torrent(torrent["id"], status="error", error=str(e))
        time.sleep(POLL_INTERVAL)
