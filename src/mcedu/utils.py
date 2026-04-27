"This is where general utility functions will go."
from functools import cache
from uuid import uuid4
import struct
import random
import string

uuid=lambda: str(uuid4())
paramstring=lambda l: ",".join([x for x in l if x!=""])
paramaker=lambda x,y: f"{x}={y}"

def generatePlayfabID():
    """
    Generates a custom ID for the player.

    Returns:
        str: A custom ID string prefixed with 'MCPF' and followed by 16 hex-encoded bytes.
    """
    return "MCPF" + binascii.hexlify(os.urandom(16)).decode("UTF-8").upper()

def generateDeviceID() -> str:
    """
    Generates a DeviceID.
    
    Returns:
        str: A device ID which is 32 random hex-encoded bytes.
    """
    return ''.join( random.choice(string.hexdigits) for _ in range(32) ).lower()
