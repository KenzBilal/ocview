"""Window state persistence and screen detection."""

import json
import gi

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from config.settings import STATE_FILE, CONFIG_DIR


def load_state():
    """Read state.json, returns dict or empty dict if missing."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(x, y, width, height, watch_dir=None):
    """Write window geometry (and optional watch_dir) to state.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state.update({"x": x, "y": y, "width": width, "height": height})
    if watch_dir is not None:
        state["watch_dir"] = watch_dir
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def save_watch_dir(path):
    """Save watch_dir to state.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state["watch_dir"] = path
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def clear_watch_dir():
    """Remove watch_dir from state.json."""
    state = load_state()
    state.pop("watch_dir", None)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_screen_resolution():
    """Returns (width, height) of the primary monitor."""
    display = Gdk.Display.get_default()
    monitor = display.get_monitor(0)
    geometry = monitor.get_geometry()
    return geometry.width, geometry.height
