# Nano Hermes

A minimal personal fork of [HKUDS/nanobot](https://github.com/HKUDS/nanobot).

This repository keeps the Python agent runtime, CLI, tests, templates, and built-in skills, while removing upstream marketing assets, web UI sources, Docker deployment files, long-form docs, issue templates, and the bundled WhatsApp TypeScript bridge.

## What is included

- Python package: `nanobot/`
- CLI entry point: `nanobot`
- Agent runtime, memory, tools, sessions, providers, channels, and templates
- Test suite: `tests/`
- Packaging metadata: `pyproject.toml`

## What was intentionally removed

- Demo GIFs and README images
- Upstream docs site content
- GitHub issue templates and community files
- Dockerfile / docker-compose deployment setup
- React/Vite Web UI source tree
- Bundled WhatsApp Node/TypeScript bridge

The code still contains some optional channel/provider integrations from upstream. They can be pruned later if this fork settles on a smaller supported surface.

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
nanobot onboard --wizard
```

Or create the default config non-interactively:

```bash
nanobot onboard
```

By default, user config/runtime data lives under `~/.nanobot`.

## Usage

Send a one-off message:

```bash
nanobot agent -m "Hello"
```

Start an interactive session:

```bash
nanobot agent
```

Check configuration/status:

```bash
nanobot status
```

Run the OpenAI-compatible API server, if the `api` extra is installed:

```bash
python -m pip install -e '.[dev,api]'
nanobot serve
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

If WhatsApp support is needed again, restore or replace the removed `bridge/` implementation before enabling the WhatsApp channel login flow.

## License

MIT. See [LICENSE](LICENSE). Upstream third-party notices are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
