"""LangChain ReAct agent with tools."""

from datetime import datetime

import httpx
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from gertrude.devices.tv import (
    IRCC_VOLUME_DOWN,
    IRCC_VOLUME_STOP,
    IRCC_VOLUME_UP,
    send_ircc_command,
)


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def control_tv_volume(action: str) -> str:
    """Control the TV sound volume.

    Args:
        action: "up" to increase, "down" to decrease, or "stop" to mute.
    """
    action = action.lower().strip()
    command_code = None
    match action:
        case "up":
            command_code = IRCC_VOLUME_UP
        case "down":
            command_code = IRCC_VOLUME_DOWN
        case "stop":
            command_code = IRCC_VOLUME_STOP
        case _:
            return f"Error: Invalid action '{action}'. Use 'up', 'down', or 'stop'."

    try:
        send_ircc_command(command_code)
        return f"TV sound {action} executed successfully."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


TOOLS = [get_current_time, control_tv_volume]


def create_agent(model: str = "gpt-4o-mini"):
    """Create a ReAct agent with tools."""
    llm = ChatOpenAI(model=model)
    return create_react_agent(llm, TOOLS)


def run_agent_loop(agent, initial_message: str | None = None):
    """Run an interactive agent loop."""
    config = {"configurable": {"thread_id": "gertrude-session"}}

    if initial_message:
        response = agent.invoke({"messages": [HumanMessage(content=initial_message)]}, config)
        print(f"\nAgent: {response['messages'][-1].content}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye!")
            break

        response = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config)
        print(f"\nAgent: {response['messages'][-1].content}\n")
