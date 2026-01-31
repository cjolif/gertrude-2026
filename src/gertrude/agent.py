"""LangChain ReAct agent with tools."""

from datetime import datetime

import httpx
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

TV_IP = "192.168.1.11"
TV_PSK = "0000"
IRCC_VOLUME_UP = "AAAAAQAAAAEAAAASAw=="
IRCC_VOLUME_DOWN = "AAAAAQAAAAEAAAATAw=="
IRCC_VOLUME_STOP = "AAAAAQAAAAEAAAAUAw=="


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _send_ircc_command(command_code: str) -> None:
    """Send an IRCC command to the Sony Bravia TV."""
    url = f"http://{TV_IP}/sony/IRCC"
    body = (
        '<?xml version="1.0"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        "<s:Body>"
        '<u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">'
        f"<IRCCCode>{command_code}</IRCCCode>"
        "</u:X_SendIRCC>"
        "</s:Body>"
        "</s:Envelope>"
    )
    headers = {
        "Content-Type": "text/xml; charset=UTF-8",
        "SOAPACTION": '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"',
        "X-Auth-PSK": TV_PSK,
    }
    response = httpx.post(url, content=body, headers=headers, timeout=5.0)
    response.raise_for_status()


@tool
def tv_sound(action: str) -> str:
    """Increase or decrease the TV sound.

    Args:
        action: Either "up" to increase volume or "down" to decrease volume.
    """
    action = action.lower().strip()
    match action:
        case "up":
            command_code = IRCC_VOLUME_UP
        case "down":
            command_code = IRCC_VOLUME_DOWN
        case "stop":
            command_code = IRCC_VOLUME_STOP
        case _:
            return f"Error: Invalid action '{action}'. Use 'up' or 'down'."

    try:
        _send_ircc_command(command_code)
        return f"TV sound {action} executed successfully."
    except httpx.HTTPStatusError as e:
        return f"Error: TV returned HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error connecting to TV: {e}"


TOOLS = [get_current_time, tv_sound]


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
