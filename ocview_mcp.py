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
        name="open_url",
        description="Open a URL in the ocview preview panel",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to load, e.g. http://localhost:3000",
                }
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="reload_preview",
        description="Reload the current page in ocview",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="inject_javascript",
        description="Run JavaScript code in the current page and return the result. Use for DOM manipulation, reading values, or testing interactions.",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "JavaScript code to execute",
                }
            },
            "required": ["code"],
        },
    ),
    Tool(
        name="describe_page",
        description="Get an AI-friendly summary of the current page including title, headings, buttons, inputs, forms, links and any JavaScript errors",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_errors",
        description="Get all JavaScript console errors detected on the current page since last cleared",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="clear_errors",
        description="Clear the JavaScript error log",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="click_element",
        description="Click a DOM element by CSS selector",
        inputSchema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector e.g. #login-btn or .submit",
                }
            },
            "required": ["selector"],
        },
    ),
    Tool(
        name="type_into",
        description="Type text into an input field by CSS selector",
        inputSchema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of input field",
                },
                "text": {
                    "type": "string",
                    "description": "Text to type into the field",
                },
            },
            "required": ["selector", "text"],
        },
    ),
    Tool(
        name="take_screenshot",
        description="Take a screenshot of the current ocview preview panel and return it as base64 PNG. Use to visually inspect the current state of the page.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_status",
        description="Check if ocview is running and get current state including loaded URL and version",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="watch_directory",
        description="Watch a local directory for file changes and automatically reload the preview when files are modified. Perfect for live development workflow.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to watch. e.g. /home/user/myproject or ./myproject",
                }
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="stop_watching",
        description="Stop watching the current directory for file changes",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="watch_status",
        description="Check if file watching is active and which directory is being watched",
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
        if name == "open_url":
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
