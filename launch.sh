#!/bin/bash

if [ ! -d "venv" ]; then
    echo "First run detected. Installing dependencies..."

    sed -i 's/\r$//' install.sh

    chmod +x install.sh
    ./install.sh
fi

source venv/bin/activate
python3 main.py
