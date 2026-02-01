# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the agent CLI
uv run gertrude chat
uv run gertrude chat "What time is it?"
uv run gertrude chat --model gpt-4o

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_cli.py

# Run a specific test
uv run pytest tests/test_cli.py::test_version

# Lint
uv run ruff check src tests

# Format
uv run ruff format src tests

# Install pre-commit hooks (run once after cloning)
uv run pre-commit install

# Run pre-commit on all files manually
uv run pre-commit run --all-files
```

## Environment

Environment variables are loaded from `.env` file via python-dotenv.

Required:
- `OPENAI_API_KEY`: OpenAI API key

Optional:
- `TV_IP`: Sony Bravia TV IP address (default: `192.168.0.2`)
- `TV_PSK`: TV pre-shared key for authentication (default: `0000`)

## Architecture

This is a LangChain-based ReAct agent CLI using Typer.

- **src/gertrude/cli.py**: Typer CLI with `chat` command, loads `.env` at startup
- **src/gertrude/agent.py**: LangChain ReAct agent setup with tools
  - Uses `langgraph.prebuilt.create_react_agent`
  - Tools: `get_current_time`, `change_tv_volume`, `change_tv_channel`, `toggle_tv_power`
- **src/gertrude/devices/**: Device control modules
  - **tv.py**: Sony Bravia TV control via IRCC commands
- **tests/**: pytest tests for CLI and agent tools

To add new tools, define them with `@tool` decorator in `agent.py` and add to `TOOLS` list.

## TV Control

TV tools control a Sony Bravia TV via IRCC commands over HTTP.

- **change_tv_volume**: `up`, `down`, `mute`
- **change_tv_channel**: `up`, `down`, or channel number (e.g., `5`, `12`)
- **toggle_tv_power**: toggles TV on/off
