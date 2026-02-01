"""Command-line interface for Gertrude."""

import logging

import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="Gertrude - A LangChain agent CLI")


@app.command()
def chat(
    message: str | None = typer.Argument(None, help="Initial message to send to the agent"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model to use"),
    voice: bool = typer.Option(False, "--voice", help="Use voice input instead of text"),
) -> None:
    """Start an interactive chat session with the agent."""
    from gertrude.agent import init_agent, run_agent_loop

    typer.echo(f"Starting Gertrude agent (model: {model})...")
    if voice:
        typer.echo("Voice mode enabled. Press Enter to record, Enter again to stop.\n")
    else:
        typer.echo("Type 'exit' or 'quit' to end the session.\n")

    agent = init_agent(model=model)
    run_agent_loop(agent, initial_message=message, voice_mode=voice)


@app.command()
def version() -> None:
    """Show the version."""
    from gertrude import __version__

    typer.echo(f"gertrude {__version__}")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    lvl = logging.INFO if verbose else logging.WARN
    fmt = "%(message)s"
    logging.basicConfig(level=lvl, format=fmt)


if __name__ == "__main__":
    app()
