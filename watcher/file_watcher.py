"""File watcher — monitors directory for changes and triggers reload."""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_EXTENSIONS = {
    ".html", ".css", ".js", ".ts", ".jsx", ".tsx",
    ".py", ".json", ".svg", ".vue", ".svelte",
}

IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__",
    ".venv", "dist", "build", ".next",
}


class _Handler(FileSystemEventHandler):
    """Internal handler that debounces and calls the reload callback."""

    def __init__(self, on_change_callback):
        super().__init__()
        self.on_change_callback = on_change_callback
        self.last_reload = 0

    def _should_ignore(self, path):
        parts = path.split("/")
        for part in parts:
            if part in IGNORED_DIRS:
                return True
        return False

    def _is_watched(self, path):
        import os
        _, ext = os.path.splitext(path)
        return ext.lower() in WATCHED_EXTENSIONS

    def on_modified(self, event):
        if event.is_directory:
            return
        if self._should_ignore(event.src_path):
            return
        if not self._is_watched(event.src_path):
            return

        now = time.time()
        if now - self.last_reload < 0.5:
            return
        self.last_reload = now

        print(f"File changed: {event.src_path} → reloading")
        self.on_change_callback()

    def on_created(self, event):
        self.on_modified(event)


class FileWatcher:
    """Watch a directory recursively for file changes."""

    def __init__(self, watch_dir, on_change_callback):
        self.watch_dir = watch_dir
        self.on_change_callback = on_change_callback
        self.observer = Observer()
        self.handler = _Handler(on_change_callback)

    def start(self):
        self.observer.schedule(self.handler, self.watch_dir, recursive=True)
        self.observer.start()
        print(f"ocview watching: {self.watch_dir}")

    def stop(self):
        self.observer.stop()
        self.observer.join(timeout=5)
        print("ocview file watcher stopped")

    def is_running(self):
        return self.observer.is_alive()
