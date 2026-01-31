# Gertrude

A CLI tool built with Python and Typer.

## Installation

```bash
uv sync
```

## Usage

```bash
# Run the CLI
uv run gertrude --help

# Start a chat session
uv run gertrude chat
uv run gertrude chat "What time is it?"
uv run gertrude chat --model gpt-4o

# Show version
uv run gertrude version
```

## Development

```bash
# Install dependencies (including dev)
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check src tests

# Format code
uv run ruff format src tests
```
