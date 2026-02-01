"""Sony Bravia TV control via IRCC commands."""

import os

import httpx

TV_IP = os.getenv("TV_IP", "192.168.0.2")
TV_PSK = os.getenv("TV_PSK", "0000")

IRCC_VOLUME_UP = "AAAAAQAAAAEAAAASAw=="
IRCC_VOLUME_DOWN = "AAAAAQAAAAEAAAATAw=="
IRCC_VOLUME_STOP = "AAAAAQAAAAEAAAAUAw=="


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
    response = httpx.post(url, content=body, headers=headers, timeout=5.0)
    response.raise_for_status()