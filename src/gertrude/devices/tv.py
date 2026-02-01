"""Sony Bravia TV control via IRCC commands."""

import logging
import os

import httpx

LOGGER = logging.getLogger(__name__)

TV_IP = os.getenv("TV_IP", "192.168.0.2")
TV_PSK = os.getenv("TV_PSK", "0000")

# Power & Input
IRCC_POWER = "AAAAAQAAAAEAAAAVAw=="
IRCC_INPUT = "AAAAAQAAAAEAAAAlAw=="
IRCC_SYNC_MENU = "AAAAAgAAABoAAABYAw=="
IRCC_HDMI1 = "AAAAAgAAABoAAABaAw=="
IRCC_HDMI2 = "AAAAAgAAABoAAABbAw=="
IRCC_HDMI3 = "AAAAAgAAABoAAABcAw=="
IRCC_HDMI4 = "AAAAAgAAABoAAABdAw=="

# Numbers
IRCC_NUM0 = "AAAAAQAAAAEAAAAJAw=="
IRCC_NUM1 = "AAAAAQAAAAEAAAAAAw=="
IRCC_NUM2 = "AAAAAQAAAAEAAAABAw=="
IRCC_NUM3 = "AAAAAQAAAAEAAAACAw=="
IRCC_NUM4 = "AAAAAQAAAAEAAAADAw=="
IRCC_NUM5 = "AAAAAQAAAAEAAAAEAw=="
IRCC_NUM6 = "AAAAAQAAAAEAAAAFAw=="
IRCC_NUM7 = "AAAAAQAAAAEAAAAGAw=="
IRCC_NUM8 = "AAAAAQAAAAEAAAAHAw=="
IRCC_NUM9 = "AAAAAQAAAAEAAAAIAw=="
IRCC_DOT = "AAAAAgAAAJcAAAAdAw=="

# Navigation
IRCC_UP = "AAAAAQAAAAEAAAB0Aw=="
IRCC_DOWN = "AAAAAQAAAAEAAAB1Aw=="
IRCC_LEFT = "AAAAAQAAAAEAAAA0Aw=="
IRCC_RIGHT = "AAAAAQAAAAEAAAAzAw=="
IRCC_CONFIRM = "AAAAAQAAAAEAAABlAw=="
IRCC_BACK = "AAAAAgAAAJcAAAAjAw=="
IRCC_HOME = "AAAAAQAAAAEAAABgAw=="
IRCC_OPTIONS = "AAAAAgAAAJcAAAA2Aw=="
IRCC_HELP = "AAAAAgAAAMQAAABNAw=="
IRCC_DISPLAY = "AAAAAQAAAAEAAAA6Aw=="

# Volume & Audio
IRCC_VOLUME_UP = "AAAAAQAAAAEAAAASAw=="
IRCC_VOLUME_DOWN = "AAAAAQAAAAEAAAATAw=="
IRCC_MUTE = "AAAAAQAAAAEAAAAUAw=="
IRCC_AUDIO = "AAAAAQAAAAEAAAAXAw=="

# Channel
IRCC_CHANNEL_UP = "AAAAAQAAAAEAAAAQAw=="
IRCC_CHANNEL_DOWN = "AAAAAQAAAAEAAAARAw=="

# Playback
IRCC_PLAY = "AAAAAgAAAJcAAAAaAw=="
IRCC_PAUSE = "AAAAAgAAAJcAAAAZAw=="
IRCC_STOP = "AAAAAgAAAJcAAAAYAw=="
IRCC_PREV = "AAAAAgAAAJcAAAA8Aw=="
IRCC_NEXT = "AAAAAgAAAJcAAAA9Aw=="
IRCC_FLASH_PLUS = "AAAAAgAAAJcAAAB4Aw=="
IRCC_FLASH_MINUS = "AAAAAgAAAJcAAAB5Aw=="

# Color buttons
IRCC_RED = "AAAAAgAAAJcAAAAlAw=="
IRCC_GREEN = "AAAAAgAAAJcAAAAmAw=="
IRCC_YELLOW = "AAAAAgAAAJcAAAAnAw=="
IRCC_BLUE = "AAAAAgAAAJcAAAAkAw=="

# Closed captions
IRCC_CC = "AAAAAgAAAJcAAAAoAw=="


def get_power_status() -> bool:
    """Get the current power status of the Sony Bravia TV.

    Returns:
        True if the TV is on (active), False if off (standby).
    """
    url = f"http://{TV_IP}/sony/system"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-PSK": TV_PSK,
    }
    payload = {
        "method": "getPowerStatus",
        "id": 1,
        "params": [],
        "version": "1.0",
    }
    LOGGER.info(f"Getting power status from TV at {TV_IP}")
    response = httpx.post(url, json=payload, headers=headers, timeout=5.0)
    response.raise_for_status()
    result = response.json()
    status = result.get("result", [{}])[0].get("status", "")
    return status == "active"


def send_ircc_command(command_code: str) -> None:
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
    LOGGER.info(f"Sending IRCC command {command_code} to TV at {TV_IP}")
    response = httpx.post(url, content=body, headers=headers, timeout=5.0)
    if response.status_code != 200:
        LOGGER.error(f"Error sending IRCC command: {response.text}")
    response.raise_for_status()
