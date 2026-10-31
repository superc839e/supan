#!/bin/sh
cd "$(dirname "$0")" || exit 1
command -v python3 >/dev/null || { echo "Instala Python 3: sudo apt install python3 python3-tk python3-venv"; exit 1; }
exec python3 instalador.py
