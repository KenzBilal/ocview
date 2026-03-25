"""WebKitGTK WebView engine — creation, configuration, navigation."""

import base64
import io
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GLib

from config.settings import DEFAULT_URL
from webview.injector import inject_on_load

_webview = None


def init_webview():
    """Create and return a fully configured WebKitGTK WebView."""
    global _webview

    settings = WebKit2.Settings()

    # Performance: disable unnecessary features
    settings.set_enable_webgl(False)
    settings.set_media_playback_requires_user_gesture(True)
    settings.set_media_playback_allows_inline(False)
    settings.set_enable_media(False)
    settings.set_enable_java(False)
    settings.set_enable_plugins(False)
    settings.set_enable_page_cache(False)
    settings.set_javascript_can_open_windows_automatically(False)

    # Sensible defaults
    settings.set_enable_developer_extras(True)
    settings.set_enable_write_console_messages_to_stdout(True)

    # Disable disk cache via context
    context = WebKit2.WebContext.get_default()
    context.set_cache_model(WebKit2.CacheModel.DOCUMENT_VIEWER)

    _webview = WebKit2.WebView.new_with_settings(settings)
    _webview.set_hexpand(True)
    _webview.set_vexpand(True)

    # Inject error-catcher on every page load
    inject_on_load(_webview)

    # Load default URL
    _webview.load_uri(DEFAULT_URL)

    return _webview


def load_url(url):
    """Load a URL into the WebView."""
    if _webview:
        _webview.load_uri(url)


def reload():
    """Reload the current page."""
    if _webview:
        _webview.reload()


def get_current_url():
    """Return the current URL string."""
    if _webview:
        return _webview.get_uri() or ""
    return ""


def take_screenshot():
    """Capture WebView as PNG, return base64 encoded string. Must be called from GTK thread."""
    if not _webview:
        return None

    result_holder = [None]

    def _on_snapshot(webview, task, data):
        try:
            surface = webview.get_snapshot_finish(task)
            buf = io.BytesIO()
            surface.write_to_png(buf)
            result_holder[0] = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            result_holder[0] = None

    _webview.get_snapshot(
        WebKit2.SnapshotRegion.FULL_DOCUMENT,
        WebKit2.SnapshotOptions(0),
        None,
        _on_snapshot,
        None,
    )

    while result_holder[0] is None:
        GLib.MainContext.default().iteration(False)

    return result_holder[0]
