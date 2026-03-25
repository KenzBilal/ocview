"""ocview configuration constants."""

import os
from pathlib import Path

PORT = 7842
CONFIG_DIR = Path.home() / ".config" / "ocview"
STATE_FILE = CONFIG_DIR / "state.json"
DEFAULT_URL = "about:blank"
APP_NAME = "ocview"
VERSION = "0.1.0"
GITHUB_URL = "https://github.com/KenzBilal/ocview"
INSTALL_DIR = os.path.expanduser("~/.local/share/ocview")


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
