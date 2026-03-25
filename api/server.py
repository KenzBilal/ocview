"""FastAPI server — runs uvicorn in a daemon thread alongside GTK main loop."""

import threading
import uvicorn
from fastapi import FastAPI

from api.routes import router
from config.settings import PORT


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="ocview", docs_url=None, redoc_url=None)
    app.include_router(router)
    return app


app = create_app()


def start_server():
    """Launch uvicorn in the current (background) thread."""
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


def start_server_thread():
    """Start the API server in a daemon thread."""
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    return thread
