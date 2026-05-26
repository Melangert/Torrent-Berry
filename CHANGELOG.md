# Changelog

All notable changes to Swarmberry will be documented here.

## [0.1.0] - 2026-05-24

### Added
- Initial release
- BitTorrent downloading via libtorrent
- Magnet link and .torrent file support
- JWT authentication
- Auto-seeding with configurable ratio limit (default 2.0)
- Pause and resume downloads
- REST API with FastAPI
- Web UI with auto-refresh
- System status panel (CPU, RAM, disk)
- SQLite queue
- Docker and docker-compose support
- k3s/Kubernetes manifests
- Crash recovery for interrupted downloads
- Tuned defaults for low-end devices (Pi 3B and similar)

## [0.2.0] - 2026-05-25

### Changed
- Renamed from Swarmberry to Torberry
- Removed Docker and k3s — now runs directly with Python
- Simplified deployment to single process
- Frontend served directly from backend
- All env vars renamed from SWARMBERRY_ to TORBERRY_
- Default data directory changed to ~/torberry
