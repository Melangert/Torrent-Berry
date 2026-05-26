# config.py

import os
from pathlib import Path

# -- Paths --
BASE_DIR = Path(os.getenv("TORBERRY_BASE_DIR", str(Path.home() / "torberry")))
DOWNLOAD_DIR = BASE_DIR / "downloads"
INCOMPLETE_DIR = BASE_DIR / "incomplete"
DB_PATH = BASE_DIR / "db" / "torberry.db"

# Create directories if they don't exist
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
INCOMPLETE_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "db").mkdir(parents=True, exist_ok=True)

# -- API --
API_HOST = os.getenv("TORBERRY_HOST", "0.0.0.0")
API_PORT = int(os.getenv("TORBERRY_PORT", "8080"))
SECRET_KEY = os.getenv("TORBERRY_SECRET_KEY", "changeme")
TOKEN_EXPIRE_HOURS = int(os.getenv("TORBERRY_TOKEN_EXPIRE_HOURS", "24"))

# -- Auth --
ADMIN_USERNAME = os.getenv("TORBERRY_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("TORBERRY_PASSWORD", "admin")

# -- libtorrent -- tuned for low end hardware
LT_DOWNLOAD_LIMIT = int(os.getenv("TORBERRY_DL_LIMIT", "0"))
LT_UPLOAD_LIMIT = int(os.getenv("TORBERRY_UL_LIMIT", "0"))
LT_MAX_CONNECTIONS = int(os.getenv("TORBERRY_MAX_CONNECTIONS", "50"))
LT_MAX_UPLOADS = int(os.getenv("TORBERRY_MAX_UPLOADS", "4"))
LT_LISTEN_PORT = int(os.getenv("TORBERRY_LISTEN_PORT", "6881"))

# -- Queue --
POLL_INTERVAL = float(os.getenv("TORBERRY_POLL_INTERVAL", "2.0"))
