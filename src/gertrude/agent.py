"""LangChain ReAct agent with tools."""

import logging
import os
from datetime import datetime

import httpx
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

from gertrude.devices.tv import (
    IRCC_CHANNEL_DOWN,
    IRCC_CHANNEL_UP,
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
    call_rest_api,
    send_ircc_command,
)

LOGGER = logging.getLogger(__name__)

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


def _get_volume_info() -> dict:
    """Get the current volume information (internal helper)."""
    result = call_rest_api("audio", "getVolumeInformation")
    volumes = result.get("result", [[]])[0]
    # for now we only care about the first target (speaker)
    return {
        "volume": volumes[0].get("volume", 0),
        "mute": volumes[0].get("mute", False),
    }


def _set_volume(volume: int, target: str = "speaker") -> None:
    """Set the TV volume to a specific level (0-100)."""
    volume = max(0, min(100, volume))
    call_rest_api("audio", "setAudioVolume", [{"volume": str(volume), "target": target}])


@tool
def get_tv_volume() -> str:
    """Get the current TV volume level and mute status."""
    try:
        info = _get_volume_info()
        mute_status = " (muted)" if info["mute"] else ""
        return f"Volume: {info['volume']}{mute_status}"
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def change_tv_volume(action: str) -> str:
    """Change the TV sound volume.

    Args:
        action: "up" to increase by 5, "down" to decrease by 5, or a number (0-100)
            to set specific level.
    """
    action = action.lower().strip()

    try:
        if action == "up":
            info = _get_volume_info()
            new_volume = min(100, info["volume"] + 5)
            _set_volume(new_volume)
            return f"Volume increased to {new_volume}."
        elif action == "down":
            info = _get_volume_info()
            new_volume = max(0, info["volume"] - 5)
            _set_volume(new_volume)
            return f"Volume decreased to {new_volume}."
        elif action.isdigit():
            level = int(action)
            if not 0 <= level <= 100:
                return "Error: Volume must be between 0 and 100."
            _set_volume(level)
            return f"Volume set to {level}."
        else:
            return f"Error: Invalid action '{action}'. Use 'up', 'down', or 0-100."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


@tool
def set_tv_mute(mute: bool) -> str:
    """Mute or unmute the TV.

    Args:
        mute: True to mute, False to unmute.
    """
    try:
        call_rest_api("audio", "setAudioMute", [{"status": mute}])
        return f"TV {'muted' if mute else 'unmuted'}."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


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
def get_tv_power_status() -> str:
    """Get the current power status of the TV."""
    try:
        result = call_rest_api("system", "getPowerStatus")
        status = result.get("result", [{}])[0].get("status", "")
        is_on = status == "active"
        return f"TV is currently {'on' if is_on else 'off'}."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


@tool
def set_tv_power(power_on: bool) -> str:
    """Turn the TV on or off.

    Args:
        power_on: True to turn on, False to turn off (standby).
    """
    try:
        call_rest_api("system", "setPowerStatus", [{"status": power_on}])
        return f"TV turned {'on' if power_on else 'off'}."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


TOOLS = [
    get_current_time,
    get_tv_volume,
    change_tv_volume,
    set_tv_mute,
    change_tv_channel,
    get_tv_power_status,
    set_tv_power,
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
