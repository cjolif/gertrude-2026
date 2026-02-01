"""LangChain ReAct agent with tools."""

import logging
import os
from datetime import datetime
from typing import Annotated

import httpx
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import InjectedState

from gertrude.devices.tv import (
    IRCC_CHANNEL_DOWN,
    IRCC_CHANNEL_UP,
    IRCC_MUTE,
    IRCC_NUM0,
    IRCC_NUM1,
    IRCC_NUM2,
    IRCC_NUM3,
    IRCC_NUM4,
    IRCC_NUM5,
    IRCC_NUM6,
    IRCC_NUM7,
    IRCC_NUM8,
    IRCC_NUM9,
    IRCC_POWER,
    IRCC_VOLUME_DOWN,
    IRCC_VOLUME_UP,
    get_power_status,
    send_ircc_command,
)

LOGGER = logging.getLogger(__name__)


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def change_tv_volume(action: str) -> str:
    """Change the TV sound volume.

    Args:
        action: "up" to increase, "down" to decrease, or "mute" to mute.
    """
    action = action.lower().strip()
    command_code = None
    match action:
        case "up":
            command_code = IRCC_VOLUME_UP
        case "down":
            command_code = IRCC_VOLUME_DOWN
        case "mute":
            command_code = IRCC_MUTE
        case _:
            return f"Error: Invalid action '{action}'. Use 'up', 'down', or 'mute'."

    try:
        send_ircc_command(command_code)
        return f"TV sound {action} executed successfully."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


DIGIT_CODES = [
    IRCC_NUM0,
    IRCC_NUM1,
    IRCC_NUM2,
    IRCC_NUM3,
    IRCC_NUM4,
    IRCC_NUM5,
    IRCC_NUM6,
    IRCC_NUM7,
    IRCC_NUM8,
    IRCC_NUM9,
]


@tool
def change_tv_channel(channel: str) -> str:
    """Change the TV channel.

    Args:
        channel: "up" to go up, "down" to go down, or a channel number (e.g., "5", "12").
    """
    channel = channel.lower().strip()

    try:
        if channel == "up":
            send_ircc_command(IRCC_CHANNEL_UP)
            return "TV channel up executed successfully."
        elif channel == "down":
            send_ircc_command(IRCC_CHANNEL_DOWN)
            return "TV channel down executed successfully."
        elif channel.isdigit():
            for digit in channel:
                send_ircc_command(DIGIT_CODES[int(digit)])
            return f"TV channel {channel} executed successfully."
        else:
            return f"Error: Invalid channel '{channel}'. Use 'up', 'down', or a number."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


@tool
def get_tv_power_status() -> any:
    """Get the current power status of the TV."""
    try:
        is_on = get_power_status()
        return f"TV is currently {'on' if is_on else 'off'}."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


@tool
def toggle_tv_power(state: Annotated[dict, InjectedState]) -> str:
    """Toggle the TV power state (on to off, or off to on).

    Note: Check the current state before toggling to know the resulting state.
    """
    try:
        send_ircc_command(IRCC_POWER)
        return "TV power toggled successfully."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


TOOLS = [
    get_current_time,
    change_tv_volume,
    change_tv_channel,
    get_tv_power_status,
    toggle_tv_power,
    TavilySearch(max_results=3, tavily_api_key=os.getenv("TAVILY_API_KEY")),
]


def init_agent(model: str = "gpt-4o-mini"):
    """Create a ReAct agent with tools."""
    llm = ChatOpenAI(model=model)
    return create_agent(model=llm, tools=TOOLS, checkpointer=InMemorySaver())


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
