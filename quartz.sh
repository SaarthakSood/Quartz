#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "First run: setting up QuartZ (about 1 GB download)..."
  python3 -m venv .venv || { echo "Python 3.10+ is required."; exit 1; }
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python run_desktop.py
