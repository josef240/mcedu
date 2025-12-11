"Methods for obtaining MCTOKEN"
from ..config import get_config, DisplayVersion, VerifyHTTPS
from .token import TokenType, Token
from .playfab import PlayFabClient
from ..utils import uuid
import requests
import random
import string
import os

def generateDeviceID():
    "Generates a DeviceID."
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

def mcSignin(custom_id="",deviceid="",sessionTicket="") -> Token:
    settings=get_config()
    head={"Connection": "Keep-Alive",
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json","User-Agent":"libhttpclient/1.0.0.0","request-id": uuid(),"session-id": settings.vector}
    custom_id = custom_id if (settings.playfabid =="") else settings.playfabid
    SessionTicket = sessionTicket if sessionTicket != "" else PlayFabClient().login_with_custom_id(custom_id)["SessionTicket"]
    DeviceID = deviceid if (deviceid != "") else (settings.deviceid if (settings.deviceid != "") else (generateDeviceID()))
    settings.deviceid=DeviceID
    SessionStartData={ 
        "device": {
            "applicationType": "MinecraftPE",
            "capabilities": None,
            "gameVersion": DisplayVersion,
            "id": DeviceID,
            "memory": "2147483864",
            "platform": "Win32",
            "playFabTitleId": "6955F",
            "storePlatform": "uwp.store",
            "treatmentOverrides": None,
            "type": "Win32"
        },
        "user": {
            "language": "en",
            "languageCode": "en-US",
            "regionCode": "US",
            "token": SessionTicket,
            "tokenType": "PlayFab"
        }
    }
    StartSession=requests.post("https://authorization.franchise.minecraft-services.net/api/v1.0/session/start",json=SessionStartData,headers=head,verify=VerifyHTTPS)
    StartSession.raise_for_status()
    AuthResponse:dict=StartSession.json()
    return Token(TokenType.MCTOKEN,AuthResponse)