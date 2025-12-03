"""
Desktop launcher that wraps the existing Flask web app in a lightweight browser window.

How it works:
- Starts the Flask app on a free localhost port (served by Waitress for stability).
- Opens the URL inside an embedded pywebview window (falls back to system browser if WebView fails).

This keeps the web UI unchanged while allowing packaging into executables on
Windows, macOS, and Linux.
"""

from __future__ import annotations

import platform
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib import request as url_request, error as url_error

import webview
from waitress import serve


# Ensure src/ is on the path so imports work both locally and in packaged builds.
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR.parent / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

# Import the Flask app defined in src/app/web.py
from app.web import app as flask_app  # type: ignore


def find_free_port() -> int:
    """Return an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(url: str, timeout: float = 10.0) -> bool:
    """Poll the given URL until it responds or timeout elapses."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with url_request.urlopen(url, timeout=1):
                return True
        except url_error.URLError:
            time.sleep(0.2)
    return False


def start_flask_server(port: int) -> None:
    """Run the Flask app with Waitress in a background thread."""
    flask_app.config["ENV"] = "production"
    flask_app.config["DEBUG"] = False
    server_thread = threading.Thread(
        target=serve,
        args=(flask_app,),
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    )
    server_thread.start()


def get_asset_path(filename: str) -> str | None:
    """
    Resolve the path to a static asset (e.g., icon), handling both
    local development and PyInstaller builds.
    """
    # 1. Check if running in a PyInstaller bundle
    if hasattr(sys, "_MEIPASS"):
        # In a one-file build, assets are unpacked to sys._MEIPASS
        # We assume the user adds data as "src/app/<file>;app"
        candidate = Path(sys._MEIPASS) / "app" / filename
        if candidate.exists():
            return str(candidate)

    # 2. Check local source structure
    # BASE_DIR is 'desktop/', so we go up one level to root, then src/app
    local_path = BASE_DIR.parent / "src" / "app" / filename
    if local_path.exists():
        return str(local_path)

    return None


def open_window(url: str) -> None:
    """Try to open the embedded window; fall back to system browser if needed."""
    # Determine correct icon extension for the OS
    system = platform.system()
    if system == "Windows":
        icon_filename = "tolerance-fir-verifier.ico"
    elif system == "Darwin":  # macOS
        icon_filename = "tolerance-fir-verifier.icns"
    else:  # Linux
        icon_filename = "tolerance-fir-verifier.png"

    icon_path = get_asset_path(icon_filename)

    try:
        # Attempt to create the window with the icon if available
        if icon_path:
            try:
                webview.create_window(
                    "Tolerance Fit Verifier",
                    url,
                    width=1043,
                    height=800,
                    icon=icon_path,
                )
            except Exception as e:
                print(f"[desktop] Failed to create window with icon ({e}). Retrying without icon.", file=sys.stderr)
                webview.create_window(
                    "Tolerance Fit Verifier",
                    url,
                    width=1043,
                    height=800,
                )
        else:
            # If the specific icon for the OS is not found, try the png as a fallback (might work on some Linux/macOS setups)
            fallback_path = get_asset_path("tolerance-fir-verifier.png")
            if fallback_path and system != "Windows":
                 webview.create_window(
                    "Tolerance Fit Verifier",
                    url,
                    width=1043,
                    height=800,
                    icon=fallback_path,
                )
            else:
                webview.create_window(
                    "Tolerance Fit Verifier",
                    url,
                    width=1043,
                    height=800,
                )

        webview.start()
    except Exception as exc:  # noqa: BLE001 - surface any UI init errors
        print(
            f"[desktop] pywebview failed to start ({exc}). "
            "Falling back to the default browser.",
            file=sys.stderr,
        )
        webbrowser.open(url)


def main() -> None:
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    start_flask_server(port)
    if not wait_for_server(url, timeout=15.0):
        print(
            "[desktop] Could not reach the local server. "
            "Check that all dependencies are installed and not blocked by firewall.",
            file=sys.stderr,
        )
        try:
            # Surface Werkzeug/Flask startup errors, if any
            # Attempt a single request to see the exact exception
            with url_request.urlopen(url, timeout=1):
                pass
        except Exception as exc:
            print(f"[desktop] Server start error: {exc}", file=sys.stderr)
        sys.exit(1)

    open_window(url)


if __name__ == "__main__":
    main()
