# 🪽 Nano Hermes

A lightweight, personal AI assistant that learns and evolves through interaction, designed for speed, privacy, and flexibility.

Nano Hermes provides a robust Python agent runtime that can be deployed across multiple chat channels, equipped with memory, long-running background subagents, and a rich set of built-in tools.

## ✨ Features

- **Multi-Channel**: Native support for Discord, Telegram, Matrix, Email, and WebSockets.
- **Subagents**: Spawn independent background tasks that report back when complete.
- **Persistent Memory**: Durable session history and long-term memory management.
- **Extensible Tools**: Easily add new capabilities (Shell, Web Search, Filesystem, etc.).
- **Protocol Support**: Built-in Model Context Protocol (MCP) support.
- **API Server**: OpenAI-compatible API surface for integration with other apps.

## 🚀 Quick Start

### Requirements

- Python 3.11+
- An API key for your preferred provider (Anthropic, OpenAI, Azure, etc.)

### Installation

```bash
# Clone the repository
git clone git@github.com:timothyckl/nano-hermes.git
cd nano-hermes

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development and API extras
pip install -e '.[dev,api,discord]'
```

### Configuration

Initialize your workspace and configure your first model:

```bash
nano-hermes onboard --wizard
```

By default, all configuration and runtime data are stored in `~/.nano-hermes`.

## 🛠️ Usage

### CLI Agent
Interact with your assistant directly in the terminal:

```bash
# One-off message
nano-hermes agent -m "Summarize my recent git logs"

# Interactive session
nano-hermes agent
```

### Serve API
Run an OpenAI-compatible server:

```bash
nano-hermes serve
```

### Status Check
Verify your configuration and connectivity:

```bash
nano-hermes status
```

## 🧪 Development

### Running Tests
Ensure everything is working correctly:

```bash
python -m pytest
```

### Linting
Maintain code quality:

```bash
ruff check nano_hermes
```

## 📄 License

MIT. See [LICENSE](LICENSE) for details.
