"""Run QuartZ as a desktop app: starts the local server and opens it in its own
window (Chrome/Edge "app mode", no tabs or address bar). Closing the window stops the server.
Set QUARTZ_NO_WINDOW=1 to only run the server."""
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn

HOST = "127.0.0.1"
PORT = int(os.getenv("QUARTZ_PORT", "7860"))
URL = f"http://{HOST}:{PORT}"


def find_browser():
    sysname = platform.system()
    if sysname == "Windows":
        roots = [os.environ.get(k, "") for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
        rel = [r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe",
               r"BraveSoftware\Brave-Browser\Application\brave.exe"]
        for r in roots:
            for x in rel:
                p = Path(r) / x
                if r and p.exists():
                    return str(p)
    elif sysname == "Darwin":
        for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"):
            if Path(p).exists():
                return p
    else:
        for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
            p = shutil.which(n)
            if p:
                return p
    return None


def wait_ready(timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen(URL + "/api/status", timeout=2).read()
            return True
        except Exception:  # noqa: BLE001
            time.sleep(0.4)
    return False


def main():
    os.chdir(Path(__file__).resolve().parent)
    server = uvicorn.Server(uvicorn.Config("backend.app:app", host=HOST, port=PORT, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    if not wait_ready():
        sys.exit(f"QuartZ server did not start. Is port {PORT} already in use? (set QUARTZ_PORT to change it)")
    print(f"QuartZ running at {URL}  (models load in the background on first start)")
    browser = None if os.getenv("QUARTZ_NO_WINDOW") else find_browser()
    try:
        if browser:
            profile = Path.home() / ".quartz" / "profile"
            profile.mkdir(parents=True, exist_ok=True)
            proc = subprocess.Popen([browser, f"--app={URL}", f"--user-data-dir={profile}",
                                     "--window-size=1200,800", "--no-first-run", "--no-default-browser-check"])
            proc.wait()  # own profile => own process => returns when the window closes
        else:
            if not os.getenv("QUARTZ_NO_WINDOW"):
                webbrowser.open(URL)
            print("Press Ctrl+C to stop.")
            while thread.is_alive():
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.should_exit = True
        thread.join(5)


if __name__ == "__main__":
    main()
