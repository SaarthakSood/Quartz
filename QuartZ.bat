@echo off
cd /d "%~dp0"
if not exist .venv (
  echo First run: setting up QuartZ. This downloads about 1 GB, please wait...
  python -m venv .venv || (echo Python 3.10+ is required. Install it from python.org & pause & exit /b 1)
  .venv\Scripts\python -m pip install --upgrade pip
  .venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
  .venv\Scripts\pip install -r requirements.txt
)
.venv\Scripts\python run_desktop.py
