# Contributing to ocview

Thank you for your interest in contributing! ocview is built for the OpenCode community and your help makes it better for everyone.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Install dependencies
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ocview.git
cd ocview

# Create virtual environment
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run ocview
python main.py
```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Keep lines under 120 characters
- Add comments for complex logic
- Keep functions small and focused
- No print debug statements in final code

## Testing

Before submitting a PR, verify:

- [ ] `ocview --version` prints version
- [ ] `ocview --help` prints help
- [ ] Window opens on the right side of screen
- [ ] `curl localhost:7842/status` returns JSON
- [ ] All 13 MCP tools work
- [ ] File watcher auto-reloads on change

## What We Need Help With

- Testing on different Linux distros and versions
- Adding new MCP tools for more AI capabilities
- Performance improvements and memory optimization
- Documentation and examples
- Bug reports with detailed reproduction steps

## Questions?

Open a [GitHub Discussion](https://github.com/anomalyco/ocview/discussions) — we're friendly!
