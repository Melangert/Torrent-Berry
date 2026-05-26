# api/routes/status.py

from fastapi import APIRouter, Depends
from api.deps import require_auth
from config import BASE_DIR
import psutil

router = APIRouter()

@router.get("/")
def get_status(username: str = Depends(require_auth)):
    disk = psutil.disk_usage(str(BASE_DIR))
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
    }
