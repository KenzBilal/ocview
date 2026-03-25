"""MCP server — exposes ocview as native tools for OpenCode AI."""

import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config.settings import PORT, VERSION

API = f"http://127.0.0.1:{PORT}"
TIMEOUT = 10.0

app = Server("ocview")

NOT_RUNNING = "ocview is not running. Start it with: python main.py"


async def _api(method: str, path: str, json: dict | None = None):
    """Call the ocview API, return response dict or None on failure."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if method == "GET":
                resp = await client.get(f"{API}{path}")
            else:
                resp = await client.post(f"{API}{path}", json=json or {})
            return resp.json()
    except httpx.ConnectError:
        return None
    except Exception:
        return None


def _err():
    return [TextContent(type="text", text=NOT_RUNNING)]


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="ocview_hint",
        description="IMPORTANT: Call this FIRST before any web work. Returns instructions that tell the AI to ALWAYS use ocview tools instead of xdg-open, browser commands, or manual previews. This is the primary way to preview web content.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="open_url",
        description="ALWAYS use this instead of xdg-open or browser commands to open URLs. Opens a URL in the ocview preview panel. Use this for any URL: localhost servers, file:// paths, or remote sites. Do NOT use xdg-open, chromium, or firefox.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to load. Can be http://localhost:3000, file:///path/to/index.html, or any URL. Use this instead of opening a browser.",
                }
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="reload_preview",
        description="Reload the current page in ocview. Use after making code changes to see updates. Prefer this over manual browser refresh.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="inject_javascript",
        description="Run JavaScript code in the ocview preview and return the result. Use this to interact with the page, read DOM values, test functionality, or modify page content. Returns the JS result as a string.",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "JavaScript code to execute in the page. e.g. 'document.title' or 'document.querySelector(\"button\").click()'",
                }
            },
            "required": ["code"],
        },
    ),
    Tool(
        name="describe_page",
        description="Get an AI-readable summary of the current page. Returns title, URL, all headings, button texts, input fields, links, form count, image count, and any JS errors. Use this to understand what the page looks like without a screenshot.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_errors",
        description="Get all JavaScript console errors captured on the current page. Use this to debug issues without needing to open browser DevTools.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="clear_errors",
        description="Clear the JavaScript error log so you can start fresh checking for new errors.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="click_element",
        description="Click a DOM element by CSS selector in the ocview preview. Use to test buttons, links, and interactive elements. Example selectors: #submit-btn, .menu-toggle, a[href='/about']",
        inputSchema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element to click. e.g. #login-btn, .submit, button[type='submit']",
                }
            },
            "required": ["selector"],
        },
    ),
    Tool(
        name="type_into",
        description="Type text into an input field by CSS selector in the ocview preview. Use to fill forms, search boxes, and text inputs. Example selectors: #email, input[name='phone'], .search-bar",
        inputSchema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the input field. e.g. #email, input[name='phone']",
                },
                "text": {
                    "type": "string",
                    "description": "Text to type into the field.",
                },
            },
            "required": ["selector", "text"],
        },
    ),
    Tool(
        name="take_screenshot",
        description="Capture a full-page screenshot of the ocview preview as base64 PNG. Use this to visually inspect the current page state, check layout, colors, and UI. Always use this instead of asking the user for screenshots.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_status",
        description="Check if ocview is running, what URL is loaded, and current version. Use this to verify ocview is available before other operations.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="watch_directory",
        description="Watch a project directory for file changes and auto-reload the preview. Use this for live development — the preview updates instantly when files are saved. This is how you do live preview during development.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the project directory. e.g. /home/user/my-project",
                }
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="stop_watching",
        description="Stop watching the current directory for file changes.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="watch_status",
        description="Check if file watching is active and which directory is being watched.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "ocview_hint":
            hint = """OCVIEW INSTRUCTIONS — Follow these rules strictly:

1. ALWAYS use ocview tools instead of browser commands (xdg-open, chromium, firefox, google-chrome).
2. To preview ANY webpage: use open_url tool.
3. To see what's on a page: use describe_page tool.
4. To check if things work: use take_screenshot tool.
5. To test interactions: use click_element and type_into tools.
6. To debug issues: use get_errors tool.
7. For live development: use watch_directory tool.
8. NEVER use xdg-open, chromium, firefox, or any shell browser command.
9. NEVER ask the user to open a browser — you can preview everything yourself via ocview.
10. When creating or editing web files, ALWAYS open them in ocview to show the result.

These tools give you eyes on the web. Use them for every web-related task."""
            return [TextContent(type="text", text=hint)]

        elif name == "open_url":
            url = arguments.get("url", "")
            data = await _api("POST", "/open", {"url": url})
            if data is None:
                return _err()
            return [TextContent(type="text", text=f"Opened {url} in ocview")]

        elif name == "reload_preview":
            data = await _api("POST", "/reload")
            if data is None:
                return _err()
            return [TextContent(type="text", text="Preview reloaded successfully")]

        elif name == "inject_javascript":
            code = arguments.get("code", "")
            data = await _api("POST", "/inject", {"code": code})
            if data is None:
                return _err()
            result = data.get("result", "null")
            return [TextContent(type="text", text=str(result))]

        elif name == "describe_page":
            data = await _api("GET", "/describe")
            if data is None:
                return _err()
            lines = [
                f"Page: {data.get('title', '')}",
                f"URL: {data.get('url', '')}",
                f"Headings: {', '.join(data.get('headings', []))}",
                f"Buttons: {', '.join(data.get('buttons', []))}",
                f"Inputs: {', '.join(data.get('inputs', []))}",
                f"Forms: {data.get('forms', 0)}",
                f"Links: {len(data.get('links', []))}",
                f"Images: {data.get('images', 0)}",
                f"Errors: {len(data.get('errors', []))} detected",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_errors":
            data = await _api("GET", "/errors")
            if data is None:
                return _err()
            errors = data.get("errors", [])
            if not errors:
                return [TextContent(type="text", text="No errors detected")]
            lines = []
            for i, e in enumerate(errors):
                lines.append(f"[{i}] {e.get('msg', '')} (in {e.get('src', 'unknown')} at line {e.get('line', 0)})")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "clear_errors":
            data = await _api("POST", "/errors/clear")
            if data is None:
                return _err()
            return [TextContent(type="text", text="Error log cleared")]

        elif name == "click_element":
            selector = arguments.get("selector", "")
            data = await _api("POST", "/click", {"selector": selector})
            if data is None:
                return _err()
            return [TextContent(type="text", text=f"Clicked element: {selector}")]

        elif name == "type_into":
            selector = arguments.get("selector", "")
            text = arguments.get("text", "")
            data = await _api("POST", "/type", {"selector": selector, "text": text})
            if data is None:
                return _err()
            return [TextContent(type="text", text=f"Typed into {selector}: {text}")]

        elif name == "take_screenshot":
            data = await _api("GET", "/screenshot")
            if data is None:
                return _err()
            b64 = data.get("image", "")
            if not b64:
                return [TextContent(type="text", text="Screenshot failed: no image data")]
            return [TextContent(type="text", text=f"data:image/png;base64,{b64}")]

        elif name == "get_status":
            data = await _api("GET", "/status")
            if data is None:
                return _err()
            errors_data = await _api("GET", "/errors")
            err_count = len(errors_data.get("errors", [])) if errors_data else 0
            lines = [
                f"ocview v{data.get('version', VERSION)} is running",
                f"Current URL: {data.get('url', 'unknown')}",
                f"API Port: {data.get('port', PORT)}",
                f"Errors logged: {err_count}",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "watch_directory":
            path = arguments.get("path", "")
            data = await _api("POST", "/watch", {"path": path})
            if data is None:
                return _err()
            if data.get("status") == "error":
                return [TextContent(type="text", text=data.get("message", "Failed to start watcher"))]
            return [TextContent(type="text", text=data.get("message", f"Now watching {path} for changes"))]

        elif name == "stop_watching":
            data = await _api("POST", "/watch/stop")
            if data is None:
                return _err()
            return [TextContent(type="text", text=data.get("message", "File watcher stopped"))]

        elif name == "watch_status":
            data = await _api("GET", "/watch/status")
            if data is None:
                return _err()
            watching = data.get("watching", False)
            path = data.get("path", "none") or "none"
            exts = ", ".join(data.get("extensions", []))
            lines = [
                f"Watching: {'yes' if watching else 'no'}",
                f"Path: {path}",
                f"Extensions: {exts}",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error calling {name}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def run_mcp_server():
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
