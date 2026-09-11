"""`python -m prusa_pa_tuner` — start the server and open a browser."""
from __future__ import annotations

import argparse
import ctypes
import logging
import os
import signal
import sys
import threading
import time
import webbrowser

import uvicorn

from . import __version__
from .config import config_path, load_config

_CTRL_CLOSE_EVENT = 2
_CLOSE_SHUTDOWN_TIMEOUT_S = 4.0


def _handle_console_event(event: int, shutdown_complete: threading.Event) -> bool:
    if event != _CTRL_CLOSE_EVENT:
        return False
    signal.raise_signal(signal.SIGINT)
    # ponytail: Windows allows five seconds; use a service if cleanup ever needs longer.
    shutdown_complete.wait(timeout=_CLOSE_SHUTDOWN_TIMEOUT_S)
    return True


def _install_console_close_handler(shutdown_complete: threading.Event):
    handler_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)
    handler = handler_type(lambda event: _handle_console_event(event, shutdown_complete))
    set_handler = ctypes.windll.kernel32.SetConsoleCtrlHandler
    set_handler.argtypes = [handler_type, ctypes.c_bool]
    set_handler.restype = ctypes.c_bool
    if not set_handler(handler, True):
        raise ctypes.WinError()
    return handler


def main() -> int:
    parser = argparse.ArgumentParser(prog="prusa-pa-tuner", description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port (default 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open the browser")
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    cfg = load_config()
    print(f"PrusaPATuner v{__version__}")
    print(f"  config: {config_path()}")
    print(f"  http:   http://{args.host}:{args.port}/")
    print(f"  udp:    listening on port {cfg.udp_port}")
    print()

    if not args.no_browser:
        def _open():
            time.sleep(0.8)
            try:
                webbrowser.open(f"http://{args.host}:{args.port}/")
            except Exception:
                pass

        threading.Thread(target=_open, daemon=True).start()

    shutdown_complete = threading.Event()
    close_handler = None
    if os.name == "nt" and os.environ.get("PRUSA_PA_TUNER_HANDLE_CONSOLE_CLOSE") == "1":
        close_handler = _install_console_close_handler(shutdown_complete)

    try:
        uvicorn.run(
            "prusa_pa_tuner.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
        )
    finally:
        shutdown_complete.set()
        if close_handler is not None:
            ctypes.windll.kernel32.SetConsoleCtrlHandler(close_handler, False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
