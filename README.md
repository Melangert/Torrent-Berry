# 🫐 Torberry

A light BitTorrent client designed for lowend Linux devices like  Raspberry Pis.
Simple to install

![Torrent Berry --list](Torrent-Berry.png) 

## Features

- basic Magnet link and .torrent file 
- Web UI accessible from any device on your network
- JWT authentication
- System status panel (CPU, RAM, disk)
- Crash recovery for interrupted downloads 
- Tuned for Low ram and cpu

## Requirements

- Linux (ARM or x86)
- Python 3.11+
- 512MB RAM minimum, 1GB recommended

## Install

### Quick install
```bash
git clone https://github.com/Melangert/Torrent-Berry
cd Torrent-Berry
chmod +x install.sh
sed -i 's/\r$//' install.sh
./install.sh
```

Then open `http://localhost:8080` in your browser.

## Configuration

All configuration is done via environment variables:

| Variable | Default | Description |
|---|---|---|
| TORBERRY_BASE_DIR | ~/torberry | Base directory for all data |
| TORBERRY_HOST | 0.0.0.0 | API host |
| TORBERRY_PORT | 8080 | API port |
| TORBERRY_SECRET_KEY | changeme | JWT signing key — **must be changed in production** |
| TORBERRY_USERNAME | admin | Login username |
| TORBERRY_PASSWORD | admin | Login password |
| TORBERRY_DL_LIMIT | 0 | Download limit in bytes/s (0 = unlimited) |
| TORBERRY_UL_LIMIT | 0 | Upload limit in bytes/s (0 = unlimited) |
| TORBERRY_MAX_CONNECTIONS | 50 | Max peer connections |
| TORBERRY_LISTEN_PORT | 6881 | BitTorrent listen port |

## File locations

Downloaded files go to `~/torberry/downloads` by default. Change this with the `TORBERRY_BASE_DIR` env var.


Written with help from Claude

## License

MIT
