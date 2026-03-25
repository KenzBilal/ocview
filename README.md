<p align="center">
<pre>
┌─────────────────────────────────────────┐
│                                         │
│   ░█████╗░░█████╗░██╗░░░██╗██╗███████╗ │
│   ██╔══██╗██╔══██╗██║░░░██║██║██╔════╝ │
│   ██║░░██║██║░░╚═╝╚██╗░██╔╝██║█████╗░░ │
│   ██║░░██║██║░░██╗░╚████╔╝░██║██╔══╝░░ │
│   ╚█████╔╝╚█████╔╝░░╚██╔╝░░██║███████╗ │
│   ░╚════╝░░╚════╝░░░░╚═╝░░░╚═╝╚══════╝ │
│                                         │
└─────────────────────────────────────────┘
</pre>
</p>

<p align="center">
  <strong>Lightweight AI-controlled WebView panel for OpenCode</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux-orange" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10+-yellow" alt="Python">
  <img src="https://img.shields.io/badge/OpenCode-compatible-purple" alt="OpenCode">
  <img src="https://img.shields.io/badge/RAM-~150MB-brightgreen" alt="RAM">
  <img src="https://img.shields.io/badge/cost-free-brightgreen" alt="Price">
</p>

---

## What is ocview?

You're coding in OpenCode, making changes, and constantly switching to a browser tab to check if things work. Every context switch breaks your flow. You alt-tab, refresh, squint at the result, alt-tab back, and try to remember what you were doing. Multiply this by hundreds of times per session and you've lost hours to friction that shouldn't exist.

ocview eliminates this entirely. It's a native Linux WebView panel that sits permanently to the right of your OpenCode terminal. You never touch it — OpenCode's AI controls it for you. Say "open localhost:3000" and it loads. Say "describe the page" and the AI reads the DOM. Say "watch this folder" and it auto-reloads on every save. It's the missing piece between writing code and seeing results.

## ✨ Features

- 🪟 **Sits permanently to the right of OpenCode** — zero setup positioning
- 🤖 **13 MCP tools** — full AI control from OpenCode chat
- ⚡ **Auto reloads when files change** — watchdog-based with debouncing
- 💉 **JavaScript injection with return values** — run any JS, get results back
- 🐛 **Console error capture** — JS errors forwarded to OpenCode AI automatically
- 🧠 **Smart describe_page()** — AI-readable DOM summary (headings, buttons, inputs, forms, links, errors)
- 📸 **Screenshot capture** — full page as base64 PNG via MCP
- 💾 **Remembers window position** — saves and restores geometry between sessions
- 🪶 **Under 150MB RAM** — lightweight GTK + WebKit, no Electron
- 🐧 **All major distros** — Ubuntu, Debian, Fedora, Arch, Mint, openSUSE
- 💸 **Completely free** — open source, MIT license

## 🚀 Install

```bash
curl -sSL https://raw.githubusercontent.com/KenzBilal/ocview/main/install.sh | bash
```

Or clone manually:

```bash
git clone https://github.com/KenzBilal/ocview ~/.local/share/ocview
cd ~/.local/share/ocview
chmod +x install.sh && ./install.sh
```

### Supported distributions

| Distro | Status |
|--------|--------|
| Ubuntu 20.04+ | ✅ Supported |
| Debian 11+ | ✅ Supported |
| Linux Mint 20+ | ✅ Supported |
| Pop!_OS | ✅ Supported |
| Fedora 37+ | ✅ Supported |
| Arch Linux | ✅ Supported |
| Manjaro | ✅ Supported |
| openSUSE | ✅ Supported |

## ⚙️ OpenCode Setup

**Step 1:** Start the ocview window

```bash
ocview
```

**Step 2:** Add to `~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "ocview": {
      "type": "local",
      "command": ["ocview", "--mcp"],
      "enabled": true
    }
  }
}
```

**Step 3:** Restart OpenCode and talk to it

> **Pro tip:** To make OpenCode's AI always use ocview instead of a browser, add this to your `~/.config/opencode/instructions.md` (or the `instructions` field in `opencode.json`):
>
> ```
> When working on web projects, ALWAYS preview using the ocview MCP tools.
> Use open_url instead of xdg-open or browser commands.
> Use describe_page, take_screenshot, click_element to inspect and test.
> Never ask me to open a browser — preview everything yourself via ocview.
> ```

| You say | What happens |
|---------|-------------|
| `"open localhost:3000"` | Loads the URL in the preview panel |
| `"describe the current page"` | AI reads the DOM — headings, buttons, inputs, errors |
| `"watch ./my-project"` | Auto reloads on every file save |
| `"inject document.title"` | Runs JS in the page, returns the result |
| `"take a screenshot"` | Captures the preview as a PNG image |
| `"preview this file"` | Opens the file in ocview automatically |

## 🛠️ All MCP Tools

| Tool | Description | Example in OpenCode |
|------|-------------|---------------------|
| `ocview_hint` | Tell the AI to always use ocview | Automatically called on session start |
| `open_url` | Open a URL in the preview panel | "open http://localhost:5173" |
| `reload_preview` | Reload the current page | "refresh the preview" |
| `inject_javascript` | Run JS and return result | "inject document.querySelectorAll('h1').length" |
| `describe_page` | Get AI-readable page summary | "describe what's on the page" |
| `get_errors` | Get all JS console errors | "any JavaScript errors?" |
| `clear_errors` | Clear the error log | "clear the error log" |
| `click_element` | Click element by CSS selector | "click the #submit button" |
| `type_into` | Type text into input field | "type 'hello world' into #search" |
| `take_screenshot` | Capture page as base64 PNG | "screenshot the preview" |
| `get_status` | Check ocview state and URL | "is ocview running?" |
| `watch_directory` | Watch folder for auto-reload | "watch ./src for changes" |
| `stop_watching` | Stop file watching | "stop watching" |
| `watch_status` | Check watcher state | "what folder is being watched?" |

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/open` | Load a URL |
| `POST` | `/reload` | Reload current page |
| `POST` | `/inject` | Run JavaScript |
| `GET` | `/html` | Get full page HTML |
| `POST` | `/click` | Click element by selector |
| `POST` | `/type` | Type into input field |
| `GET` | `/describe` | Get page summary |
| `GET` | `/screenshot` | Get base64 PNG screenshot |
| `GET` | `/errors` | Get JS error log |
| `POST` | `/errors/clear` | Clear error log |
| `POST` | `/internal/error` | Internal error receiver |
| `GET` | `/status` | Health check |
| `POST` | `/watch` | Start file watcher |
| `POST` | `/watch/stop` | Stop file watcher |
| `GET` | `/watch/status` | Watcher status |

API runs at `http://localhost:7842`.

## 📁 Project Structure

```
ocview/
├── main.py                  # Entry point, GTK main loop, CLI commands
├── ocview_mcp.py            # MCP server with 13 tools
├── webview/
│   ├── engine.py            # WebView creation, config, navigation, screenshots
│   ├── bridge.py            # JS injection, DOM interaction, page describe
│   └── injector.py          # Error-catching JS injection on page load
├── api/
│   ├── server.py            # FastAPI + uvicorn in daemon thread
│   └── routes.py            # All REST endpoints
├── watcher/
│   └── file_watcher.py      # Watchdog-based file change detection
├── config/
│   ├── settings.py          # App constants and paths
│   └── state.py             # Window state and watch_dir persistence
├── .github/                 # GitHub templates and CI
├── install.sh               # One-command installer
├── uninstall.sh             # Clean uninstaller
├── ocview                   # Launch script
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT
└── README.md                # You are here
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `ocview` | Start the preview window |
| `ocview --mcp` | Start MCP server for OpenCode |
| `ocview --update` | Update to latest version |
| `ocview --version` | Show version |
| `ocview --help` | Show help |

## 🤝 Contributing

Contributions are welcome! ocview is built for the OpenCode community and we'd love your help making it better.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

For big changes, please open an issue first to discuss what you'd like to do. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

<p align="center">
  Built with ❤️ for the OpenCode community<br>
  If ocview helps you, give it a ⭐ on GitHub!
</p>
