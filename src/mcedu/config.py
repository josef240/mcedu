"Contains global variables & config"
# config.py
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, Optional
from .utils import uuid
import logging
import json
import os

if TYPE_CHECKING: from .auth import AuthFlow

VerifyHTTPS=True
"I use mitmproxy to look at my HTTPS requests, and cannot do it if the requests are verified."
ProtocolVersion=898
"Bedrock Protocol Number"
BuildNumber=12113200
"Internal Build Number"
DisplayVersion="1.21.132"
"The version players see ingame"

logger = logging.getLogger("mcedu.config")

class Config:
    """A singleton-like class to hold all configuration settings."""
    def __init__(self,loadFile=True,configFile="settings.json"):
        self.configFile=configFile
        self.vector = uuid()
        self.playfabid:str=""
        self.deviceid:str=""
        self.authflow:AuthFlow=None

        if loadFile: 
            try:
                self.loadSettings()
            except Exception as e:
                logger.error(f"Error loading files: {e}")

    def __str__(self):
        global ProtocolVersion, BuildNumber
        variables=[f"protocolVersion={ProtocolVersion}",f"buildNumber={BuildNumber}",f"vector={self.vector}",f"playfabid={self.playfabid}",f"deviceid={self.deviceid}"]
        if self.authflow is not None: variables.append(f"authflow={self.authflow}")
        string=f"Config["+(",".join(variables))+"]"
        return string

    def toJSON(self) -> dict:
        """
        Serializes the critical configuration data to a dictionary suitable for JSON.
        """
        # We must extract the string tokens from the AuthFlow object
        # Assuming AuthFlow has attributes like .mctoken and .mstoken with a .token attribute
        data = {
            "lastRun": datetime.now(timezone.utc).isoformat(),
            "vector": self.vector,
            "deviceid": self.deviceid,
            "playfabid": self.playfabid,
        }
        if hasattr(self.authflow,"exportTokens"): data = data|self.authflow.exportTokens(write=False)
        return data

    def saveSettings(self):
        """
        Writes the configuration to the settings.json file.
        """
        try:
            with open(self.configFile, 'w') as f:
                json.dump(self.toJSON(), f,indent=4)
            logger.info(f"Saved to {self.configFile}")
        except Exception as e:
            logger.error(f"Error saving config to JSON: {e}")

    def loadSettings(self) -> bool:
        """
        Attempts to load critical configuration data from settings.json.
        Returns True if successful, False otherwise.
        """
        if not os.path.exists(self.configFile):
            logger.warning(f"{self.configFile} not found. Will proceed with fresh initialization.")
            return False

        try:
            with open(self.configFile, 'r') as f:
                data:dict = json.load(f)

            self.settings=data
            datakeys=data.keys()
            if "vector" in datakeys: self.vector = data["vector"]
            if "deviceid" in datakeys: self.deviceid = data["deviceid"]
            if "playfabid" in datakeys:self.playfabid = data["playfabid"]

            self.imported=True
            logger.info(f"Configuration successfully loaded from {self.configFile}.")
            return True

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading config from JSON: {e}. Proceeding with fresh initialization.")
            return False

CONFIG = None

def get_config():
    """Provides access to the the global config object."""
    global CONFIG
    if not CONFIG: CONFIG = Config(loadFile=False)
    return CONFIG

def BuildNumFromTrueVersion(version:str) ->Optional[int]:
    """Find the Build Number from the true display version, which you can find this online at MCEDU's changelog.
    Args:
        version (str): True display version"""
    versionS=version.split(".")
    if not (len(versionS)>=3): return
    if not versionS[-1].isdigit(): return
    versionS[-1] = f"{int(versionS[-1]):03d}"
    modified="".join(versionS)
    return int(modified) if modified.isdigit else None

def setVersionData(protoVersion=ProtocolVersion,buildNum=BuildNumber, strVersion=DisplayVersion):
    global ProtocolVersion, BuildNumber, DisplayVersion
    ProtocolVersion=protoVersion
    BuildNumber=buildNum
    DisplayVersion=strVersion

__all__ = [
    "VerifyHTTPS",
    "ProtocolVersion",
    "BuildNumber",
    "DisplayVersion",
    "Config",
    "get_config",
    "setVersionData",
    "BuildNumFromTrueVersion"
]