"""API routes — all HTTP endpoints for controlling the WebView."""

import os
import threading
import gi

gi.require_version('GLib', '2.0')
from gi.repository import GLib
from fastapi import APIRouter
from pydantic import BaseModel

from config.settings import VERSION, PORT
from config.state import save_watch_dir, clear_watch_dir
from webview import engine, bridge
from watcher.file_watcher import FileWatcher, WATCHED_EXTENSIONS

router = APIRouter()

# Error storage — max 100 entries
error_log = []
ERROR_LOG_MAX = 100

# Active file watcher instance
active_watcher = None


# ---------------------------------------------------------------------------
# Thread-safe GTK dispatch
# ---------------------------------------------------------------------------

def _run_on_gtk(fn, *args, **kwargs):
    """Schedule fn on the GTK main thread, block until result or timeout."""
    result_holder = {"value": None}
    event = threading.Event()

    def wrapper():
        result_holder["value"] = fn(*args, **kwargs)
        event.set()
        return False  # one-shot idle callback

    GLib.idle_add(wrapper)
    event.wait(timeout=10)
    return result_holder["value"]


def _fire_on_gtk(fn, *args, **kwargs):
    """Schedule fn on GTK main thread, don't wait for result."""
    def wrapper():
        fn(*args, **kwargs)
        return False
    GLib.idle_add(wrapper)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class UrlBody(BaseModel):
    url: str

class CodeBody(BaseModel):
    code: str

class SelectorBody(BaseModel):
    selector: str

class TypeBody(BaseModel):
    selector: str
    text: str

class ErrorBody(BaseModel):
    msg: str
    src: str = "unknown"
    line: int = 0
    col: int = 0

class WatchBody(BaseModel):
    path: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/open")
def open_url(body: UrlBody):
    _fire_on_gtk(engine.load_url, body.url)
    return {"status": "ok", "url": body.url}


@router.post("/reload")
def reload_page():
    _fire_on_gtk(engine.reload)
    return {"status": "ok"}


@router.post("/inject")
def inject(body: CodeBody):
    result = _run_on_gtk(bridge.inject_js, body.code)
    return {"status": "ok", "result": result}


@router.get("/html")
def get_html():
    html = _run_on_gtk(bridge.get_html)
    return {"status": "ok", "html": html}


@router.post("/click")
def click_element(body: SelectorBody):
    _run_on_gtk(bridge.click, body.selector)
    return {"status": "ok", "selector": body.selector}


@router.post("/type")
def type_into(body: TypeBody):
    _run_on_gtk(bridge.type_text, body.selector, body.text)
    return {"status": "ok"}


@router.get("/describe")
def describe():
    result = _run_on_gtk(bridge.describe_page)
    return result


@router.get("/screenshot")
def screenshot():
    b64 = _run_on_gtk(engine.take_screenshot)
    return {"status": "ok", "image": b64}


@router.get("/errors")
def get_errors():
    return {"status": "ok", "errors": list(error_log)}


@router.post("/errors/clear")
def clear_errors():
    error_log.clear()
    return {"status": "ok"}


@router.post("/internal/error")
def internal_error(body: ErrorBody):
    entry = {"msg": body.msg, "src": body.src, "line": body.line, "col": body.col}
    error_log.append(entry)
    if len(error_log) > ERROR_LOG_MAX:
        del error_log[: len(error_log) - ERROR_LOG_MAX]
    return {"status": "ok"}


@router.get("/status")
def status():
    url = _run_on_gtk(engine.get_current_url)
    return {"status": "ok", "version": VERSION, "url": url, "port": PORT}


# ---------------------------------------------------------------------------
# File watcher endpoints
# ---------------------------------------------------------------------------

def _on_file_change():
    """Reload callback — safely called from watcher thread."""
    GLib.idle_add(lambda: (engine.reload(), False)[1])


@router.post("/watch")
def start_watch(body: WatchBody):
    global active_watcher
    watch_path = os.path.abspath(body.path)

    if not os.path.isdir(watch_path):
        return {"status": "error", "message": f"Path does not exist: {body.path}"}

    # Stop existing watcher if running
    if active_watcher is not None:
        try:
            active_watcher.stop()
        except Exception:
            pass
        active_watcher = None

    active_watcher = FileWatcher(watch_path, _on_file_change)
    active_watcher.start()
    save_watch_dir(watch_path)

    return {
        "status": "ok",
        "watching": watch_path,
        "message": f"Now watching {watch_path} for changes",
    }


@router.post("/watch/stop")
def stop_watch():
    global active_watcher

    if active_watcher is None:
        return {"status": "ok", "message": "Watcher was not running"}

    try:
        active_watcher.stop()
    except Exception:
        pass
    active_watcher = None
    clear_watch_dir()

    return {"status": "ok", "message": "File watcher stopped"}


@router.get("/watch/status")
def watch_status():
    watching = active_watcher is not None and active_watcher.is_running()
    path = active_watcher.watch_dir if active_watcher else None
    return {
        "status": "ok",
        "watching": watching,
        "path": path,
        "extensions": sorted(WATCHED_EXTENSIONS),
    }
