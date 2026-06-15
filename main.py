
print("Starting Torberry...")
from config import API_HOST, API_PORT
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socket
import threading
from db import init_db
from downloader import run
from api.routes import auth, torrents, status
from fastapi.staticfiles import StaticFiles

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ip = get_local_ip()
    print(f"Access the web UI at: http://{ip}:{API_PORT}")
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    yield

app = FastAPI(title="Torberry", lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(torrents.router, prefix="/torrents", tags=["torrents"])
app.include_router(status.router, prefix="/status", tags=["status"])

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
