# Nano Hermes

A minimal personal AI assistant.

This repository contains the Python agent runtime, CLI, tests, templates, built-in skills, and a small set of personal channels.

## What is included

- Python package: `nano_hermes/`
- CLI entry point: `nano-hermes`
- Agent runtime, memory, tools, sessions, providers, channels, and templates
- Test suite: `tests/`
- Packaging metadata: `pyproject.toml`

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
ruff check nano_hermes
```

Build the package:

```bash
python -m build
```

## License

MIT. See [LICENSE](LICENSE). Third-party notices are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
