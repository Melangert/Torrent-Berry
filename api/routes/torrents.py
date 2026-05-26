from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import shutil
from torrent_queue import add_torrent, get_all_torrents, get_torrent, update_torrent
from config import INCOMPLETE_DIR
from api.deps import require_auth
from db import get_connection


router = APIRouter()

class  MagnetRequest(BaseModel):
    magnet: str

@router.get("/")
def list_torrents(username: str = Depends(require_auth)):
    return get_all_torrents()


@router.get("/{torrent_id}")
def get_one(torrent_id: int, username: str = Depends(require_auth)):
    torrent = get_torrent(torrent_id)
    if not torrent:
        raise HTTPException(status_code=404, detail="Torrent not found")
    return torrent


@router.post("/magnet")
def add_magnet(body: MagnetRequest, username: str = Depends(require_auth)):
    if not body.magnet.startswith("magnet:"):
        raise HTTPException(status_code=400, detail="Invalid magnet link")
    torrent_id = add_torrent(body.magnet)
    return {"id": torrent_id}



@router.post("/file")
def add_file(file: UploadFile = File(...), username: str = Depends(require_auth)):
    if not file.filename.endswith(".torrent"):
        raise HTTPException(status_code=400, detail="File must be a .torrent file")
    save_path = INCOMPLETE_DIR / file.filename
    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    torrent_id = add_torrent(str(save_path))
    return {"id": torrent_id}

@router.delete("/{torrent_id}")
def delete_torrent(torrent_id: int, username: str  = Depends(require_auth)):
    torrent = get_torrent(torrent_id)
    if not torrent: 
        raise HTTPException(status_code=404, detail="Torrent not found")
    update_torrent(torrent_id, status="done")
    return {"ok": True}

@router.post("/{torrent_id}/pause")
def  pause_torrent(torrent_id: int, username: str  = Depends(require_auth)):
    torrent = get_torrent(torrent_id)
    if not torrent:
        raise HTTPException(status_code=404, detail="Torrent not found")
    update_torrent(torrent_id, status="paused")
    return {"ok": True}

@router.post("/{torrent_id}/resume")
def resume_torrent(torrent_id: int, username: str = Depends(require_auth)):
    torrent = get_torrent(torrent_id)
    if not torrent: 
         raise HTTPException(status_code=404, detail="Torrent not found")                   
    update_torrent(torrent_id, status="queued")
    return {"ok": True}

@router.delete("/{torrent_id}")
def delete_torrent(torrent_id: int, username: str = Depends(require_auth)):
    torrent = get_torrent(torrent_id)
    if not torrent:
        raise HTTPException(status_code=404, detail="Torrent not found")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM torrents WHERE id = ?", (torrent_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

