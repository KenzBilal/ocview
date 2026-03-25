"""Error-catching JavaScript injector for page loads."""

import gi

gi.require_version('WebKit2', '4.1')
from gi.repository import WebKit2

from config.settings import PORT

INJECTOR_SCRIPT = """
window.__ocview_errors = [];
window.onerror = function(msg, src, line, col, err) {
  window.__ocview_errors.push({msg: msg, src: src, line: line, col: col, timestamp: Date.now()});
  fetch('http://localhost:PORT_PLACEHOLDER/internal/error', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({msg: msg, src: src, line: line, col: col})
  }).catch(function() {});
  return false;
};
console.error = function() {
  var msg = Array.prototype.slice.call(arguments).join(' ');
  window.__ocview_errors.push({msg: msg, src: 'console', timestamp: Date.now()});
  fetch('http://localhost:PORT_PLACEHOLDER/internal/error', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({msg: msg, src: 'console'})
  }).catch(function() {});
};
""".replace("PORT_PLACEHOLDER", str(PORT))


def inject_on_load(webview):
    """Connect to load-changed signal and inject error script after page loads."""
    user_content_manager = webview.get_user_content_manager()

    script = WebKit2.UserScript(
        INJECTOR_SCRIPT,
        WebKit2.UserContentInjectedFrames.ALL_FRAMES,
        WebKit2.UserScriptInjectionTime.END,
    )
    user_content_manager.add_script(script)
