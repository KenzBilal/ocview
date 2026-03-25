"""WebView bridge — JS injection, DOM interaction, page introspection."""

import json
import gi

gi.require_version('WebKit2', '4.1')
from gi.repository import WebKit2, GLib

from webview.engine import _webview


def _get_webview():
    """Get the active WebView instance."""
    from webview import engine
    return engine._webview


def inject_js(code):
    """Run JavaScript in the page, return result as string or None."""
    webview = _get_webview()
    if not webview:
        return None

    result_holder = [None]

    def _on_result(webview, task, data):
        try:
            js_result = webview.run_javascript_finish(task)
            if js_result:
                value = js_result.get_js_value()
                if value.is_string():
                    result_holder[0] = value.to_string()
                elif value.is_number():
                    result_holder[0] = str(value.to_double())
                elif value.is_boolean():
                    result_holder[0] = str(value.to_boolean())
                elif value.is_null() or value.is_undefined():
                    result_holder[0] = None
                else:
                    result_holder[0] = value.to_string()
        except Exception as e:
            result_holder[0] = json.dumps({"error": str(e)})

    webview.run_javascript(code, None, _on_result, None)

    # Process pending events to get result synchronously
    while result_holder[0] is None:
        GLib.MainContext.default().iteration(False)

    return result_holder[0]


def get_html():
    """Return full page HTML as string."""
    result = inject_js("document.documentElement.outerHTML")
    return result or ""


def click(selector):
    """Click a DOM element by CSS selector."""
    code = f"""
    (function() {{
        var el = document.querySelector({json.dumps(selector)});
        if (el) {{ el.click(); return true; }}
        return false;
    }})()
    """
    return inject_js(code)


def type_text(selector, text):
    """Type text into an input field identified by CSS selector."""
    escaped_text = json.dumps(text)
    code = f"""
    (function() {{
        var el = document.querySelector({json.dumps(selector)});
        if (el) {{
            el.focus();
            el.value = {escaped_text};
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}
        return false;
    }})()
    """
    return inject_js(code)


def describe_page():
    """Return JSON structure describing the current page."""
    code = """
    (function() {
        var headings = [];
        document.querySelectorAll('h1, h2, h3').forEach(function(h) {
            headings.push(h.textContent.trim());
        });

        var buttons = [];
        document.querySelectorAll('button').forEach(function(b) {
            var text = b.textContent.trim();
            if (text) buttons.push(text);
        });

        var inputs = [];
        document.querySelectorAll('input, textarea').forEach(function(inp) {
            var name = inp.getAttribute('placeholder') || inp.getAttribute('name') || inp.getAttribute('type') || 'unnamed';
            inputs.push(name);
        });

        var links = [];
        document.querySelectorAll('a').forEach(function(a) {
            var text = a.textContent.trim();
            if (text) links.push(text);
        });

        var images = document.querySelectorAll('img').length;
        var forms = document.querySelectorAll('form').length;

        var errors = window.__ocview_errors || [];

        return JSON.stringify({
            title: document.title,
            url: window.location.href,
            headings: headings,
            buttons: buttons,
            inputs: inputs,
            links: links,
            forms: forms,
            errors: errors,
            images: images
        });
    })()
    """
    result = inject_js(code)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass
    return {
        "title": "",
        "url": "",
        "headings": [],
        "buttons": [],
        "inputs": [],
        "links": [],
        "forms": 0,
        "errors": [],
        "images": 0,
    }
