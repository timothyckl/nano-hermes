# Nano Hermes

A minimal personal AI assistant forked from [HKUDS/nanobot](https://github.com/HKUDS/nanobot).

This repository keeps the Python agent runtime, CLI, tests, templates, built-in skills, and a small set of personal channels, while removing upstream marketing assets, web UI sources, Docker deployment files, long-form docs, issue templates, bundled bridge code, and unused chat integrations.

## What is included

- Python package: `nanobot/`
- CLI entry point: `nano-hermes`
- Agent runtime, memory, tools, sessions, providers, channels, and templates
- Test suite: `tests/`
- Packaging metadata: `pyproject.toml`

## What was intentionally removed

- Demo GIFs and README images
- Upstream docs site content
- GitHub issue templates and community files
- Dockerfile / docker-compose deployment setup
- React/Vite Web UI source tree
- Bundled bridge code and unused chat integrations

The channel surface is intentionally limited to Matrix, Telegram, Email, Discord, and WebSocket.

## Requirements

- Python 3.11+
- An API key for at least one configured model provider

## Setup

Create and activate a virtual environment outside or inside the repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode with development tools:

```bash
python -m pip install -e '.[dev]'
```

Initialize config and workspace:

```bash
nano-hermes onboard --wizard
```

Or create the default config non-interactively:

```bash
nano-hermes onboard
```

By default, user config/runtime data lives under `~/.nano-hermes`.

## Usage

Send a one-off message:

```bash
nano-hermes agent -m "Hello"
```

Start an interactive session:

```bash
nano-hermes agent
```

Check configuration/status:

```bash
nano-hermes status
```

Run the OpenAI-compatible API server, if the `api` extra is installed:

```bash
python -m pip install -e '.[dev,api]'
nano-hermes serve
```

## Development

Run the test suite:

```bash
pytest
```

Run a focused lint check:

```bash
ruff check nanobot
```

Build the package:

```bash
python -m build
```

## Notes for this fork

This is a personal project, not a full downstream distribution of upstream nanobot. Prefer small, practical documentation in this README over restoring the deleted upstream docs and marketing assets.

The Python import package currently remains `nanobot` to reduce merge friction with upstream. Public-facing packaging and CLI usage are branded as Nano Hermes; a legacy `nanobot` console alias is retained for compatibility.

## License

MIT. See [LICENSE](LICENSE). Upstream third-party notices are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
