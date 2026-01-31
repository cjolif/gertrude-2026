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
```

## Environment

Requires `OPENAI_API_KEY` environment variable to be set.

## Architecture

This is a LangChain-based ReAct agent CLI using Typer.

- **src/gertrude/cli.py**: Typer CLI with `chat` command that starts the agent
- **src/gertrude/agent.py**: LangChain ReAct agent setup with tools
  - Uses `langgraph.prebuilt.create_react_agent`
  - Tools: `get_current_time`, `control_tv_volume`
- **tests/**: pytest tests for CLI and agent tools

To add new tools, define them with `@tool` decorator in `agent.py` and add to `TOOLS` list.

## TV Control

The `control_tv_volume` tool controls a Sony Bravia TV volume via IRCC commands over HTTP.

Configuration in `agent.py`:
- `TV_IP`: TV's IP address (default: `192.168.1.11`)
- `TV_PSK`: Pre-shared key for authentication (default: `0000`)

Actions: `up`, `down`, `stop`
