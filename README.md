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

## 🧠 How Learning Works

Nano Hermes learns by using the LLM as the learning algorithm and plain text files as persistent memory. There are no numeric weights — knowledge is accumulated and curated across three layers:

- **Consolidation** — runs every turn. When the prompt exceeds 50% of the context window, old messages are summarised into `memory/history.jsonl` and dropped from the live context.
- **AutoCompact** — runs when a session goes idle. Same as above, but triggered by inactivity. The summary is injected at the start of the next interaction.
- **Dream** — runs on a schedule. A two-phase process: Phase 1 has the LLM read accumulated history and produce tagged directives (`[USER]`, `[MEMORY]`, `[SOUL]`, `[SKILL]`, `[MEMORY-REMOVE]`); Phase 2 applies them as surgical edits to `USER.md`, `SOUL.md`, and `memory/MEMORY.md`, and writes reusable `skills/`. Every Dream run is auto-committed to git and is fully revertible. Lines in `MEMORY.md` untouched for 14+ days are flagged via `git blame` as potentially stale.

Inspired by [NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent), which shares the same `MEMORY.md`/`USER.md`/skills pattern but additionally supports RL fine-tuning of the underlying model weights. Nano Hermes trades that for stricter memory hygiene: per-run deduplication, staleness detection, and git-backed rollback.

---

## ⚙️ Configuring Dream

Dream is configured under `agents.defaults.dream` in `~/.nano-hermes/config.json`:

```json
{
  "agents": {
    "defaults": {
      "dream": {
        "modelOverride": "openrouter/anthropic/claude-3-5-haiku",
        "intervalH": 4,
        "maxBatchSize": 20,
        "maxIterations": 15,
        "annotateLineAges": true
      }
    }
  }
}
```

All options are also available as environment variables with the prefix `NANOHERMES_AGENTS__DEFAULTS__DREAM__` (e.g. `NANOHERMES_AGENTS__DEFAULTS__DREAM__MODEL_OVERRIDE`).

| Option | Default | Description |
|---|---|---|
| `modelOverride` | main agent model | Model used for both Dream phases. Useful for routing to a cheaper model. |
| `intervalH` | `2` | Run frequency in hours. Use `cron` for a custom cron expression. |
| `maxBatchSize` | `20` | Max `history.jsonl` entries processed per run. |
| `maxIterations` | `15` | Max Phase 2 tool calls before the run is cut short. |
| `annotateLineAges` | `true` | Annotate `MEMORY.md` lines with `git blame` ages. Disable if not in a git repo. |

To trigger Dream manually from a session, run `/dream`.

---

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
