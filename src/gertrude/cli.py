"""Command-line interface for Gertrude."""

import typer

app = typer.Typer(help="Gertrude - A LangChain ReAct agent CLI")


@app.command()
def chat(
    message: str | None = typer.Argument(None, help="Initial message to send to the agent"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model to use"),
) -> None:
    """Start an interactive chat session with the agent."""
    from gertrude.agent import create_agent, run_agent_loop

    typer.echo(f"Starting Gertrude agent (model: {model})...")
    typer.echo("Type 'exit' or 'quit' to end the session.\n")

    agent = create_agent(model=model)
    run_agent_loop(agent, initial_message=message)


@app.command()
def version() -> None:
    """Show the version."""
    from gertrude import __version__

    typer.echo(f"gertrude {__version__}")


if __name__ == "__main__":
    app()
