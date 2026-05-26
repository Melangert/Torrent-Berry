#!/usr/bin/env bash

set -e

echo "Installing Torrent-Berry..."

# ---------- check python ----------
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    exit 1
fi

# ---------- create virtual environment ----------
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# ---------- upgrade pip ----------
pip install --upgrade pip

# ---------- install dependencies ----------
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
fi

# ---------- create runtime directories ----------
echo "Creating data directories..."

mkdir -p data/incomplete
mkdir -p data/complete

# ---------- finish ----------
echo ""
echo "Installation complete."
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Access the web UI at:"
echo "  http://<your-device-ip>:8000"
echo ""
