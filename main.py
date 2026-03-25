"""ocview — lightweight Linux-native WebView panel for OpenCode."""

import sys
import asyncio


def run_gtk_window():
    """Launch the GTK WebView window + API server (normal mode)."""
    import gi

    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.1')
    from gi.repository import Gtk, Gdk

    from config.settings import APP_NAME, VERSION, PORT, DEFAULT_URL
    from config.state import load_state, save_state, get_screen_resolution
    from webview.engine import init_webview

    # Load saved window state
    state = load_state()

    # Create window
    window = Gtk.Window()
    window.set_title(APP_NAME)
    window.set_default_size(
        state.get("width", 800),
        state.get("height", 900),
    )

    # Restore position or auto-position to right half of screen
    if "x" in state and "y" in state:
        window.move(state["x"], state["y"])
    else:
        screen_w, screen_h = get_screen_resolution()
        half_w = screen_w // 2
        window.move(half_w, 0)
        window.set_default_size(half_w, screen_h)

    # Create and embed WebView
    webview = init_webview()
    window.add(webview)

    # Save state on every move or resize
    def on_configure_event(widget, event):
        save_state(event.x, event.y, event.width, event.height)
        return False

    window.connect("configure-event", on_configure_event)

    # Save state and exit on close
    def on_close(widget):
        x, y = widget.get_position()
        width, height = widget.get_size()
        save_state(x, y, width, height)

        # Stop file watcher cleanly before exit
        from api import routes
        if routes.active_watcher is not None:
            try:
                routes.active_watcher.stop()
            except Exception:
                pass

        Gtk.main_quit()

    window.connect("destroy", on_close)

    # Show everything
    window.show_all()

    # Start API server in background thread
    from api.server import start_server_thread
    start_server_thread()

    # Auto-resume file watcher if saved in state
    if state.get("watch_dir"):
        import os
        watch_dir = state["watch_dir"]
        if os.path.isdir(watch_dir):
            from watcher.file_watcher import FileWatcher
            from api import routes

            def _on_file_change():
                from gi.repository import GLib
                from webview import engine
                GLib.idle_add(lambda: (engine.reload(), False)[1])

            routes.active_watcher = FileWatcher(watch_dir, _on_file_change)
            routes.active_watcher.start()
            print(f"Auto-resuming file watcher on: {watch_dir}")

    print(f"ocview v{VERSION} running on port {PORT}")
    print(f"ocview API ready at http://localhost:{PORT}")
    Gtk.main()


def run_mcp_server():
    """Launch MCP server only (stdio mode for OpenCode)."""
    from ocview_mcp import run_mcp_server as _run
    asyncio.run(_run())


if __name__ == "__main__":
    if "--mcp" in sys.argv:
        run_mcp_server()
    elif "--version" in sys.argv:
        from config.settings import VERSION
        print(f"ocview v{VERSION}")
    elif "--help" in sys.argv or "-h" in sys.argv:
        from config.settings import VERSION, PORT, GITHUB_URL
        help_text = f"""ocview v{VERSION} — WebView panel for OpenCode

Usage:
  ocview              Start the preview window
  ocview --mcp        Start MCP server for OpenCode
  ocview --update     Update to latest version
  ocview --version    Show version
  ocview --help       Show this help

API running at http://localhost:{PORT}
Config: ~/.config/ocview/

OpenCode integration:
  Add to opencode.json:
  "ocview": {{
    "type": "local",
    "command": ["ocview", "--mcp"]
  }}

More info: {GITHUB_URL}"""
        print(help_text)
    elif "--update" in sys.argv:
        import subprocess
        import os
        from config.settings import VERSION, INSTALL_DIR
        print("ocview — updating to latest version...")
        # Use install dir if it exists, otherwise use the directory containing main.py
        update_dir = INSTALL_DIR if os.path.isdir(INSTALL_DIR) else os.path.dirname(os.path.abspath(__file__))
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=update_dir, capture_output=True, text=True
            )
            print(result.stdout.strip())
            if result.returncode != 0:
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=update_dir, capture_output=True, text=True
                )
                print(result.stdout.strip())
            venv_pip = os.path.join(update_dir, ".venv", "bin", "pip")
            if os.path.isfile(venv_pip):
                subprocess.run([venv_pip, "install", "-q", "-r", "requirements.txt"], cwd=update_dir)
            else:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
                    cwd=update_dir
                )
            print(f"ocview updated to latest version (v{VERSION})")
        except Exception as e:
            print(f"Update failed: {e}")
            sys.exit(1)
    else:
        run_gtk_window()
