from requests_oauthlib import OAuth2Session
from typing import Protocol
from enum import Enum
import datetime
import logging

logger=logging.getLogger("mcedu")

class TokenType(Enum):
    MCTOKEN=0
    EDUTOKEN=1
    MSACCESS=3
    IMPORTED=5

class Token:
    "Token class for holding tokens."
    def __init__(self,type:TokenType,jsonData:dict) -> None:
        self.type=type
        self.jsonData=jsonData
        self.processData(jsonData)
    
    def __str__(self) -> str:
        string=""
        properties=[
            f"type={self.type.name}",
            f"expireDate={self.expireDate}",
            f"refreshable={False if (self.refreshToken is None) else True}"
        ]
        string+=f"Token["+(",".join(properties))+"]"
        return string

    def processData(self,jsonData) -> None:
        match self.type:
            case TokenType.MSACCESS:
                self.expireDate=datetime.datetime.fromtimestamp(jsonData["expires_at"],tz=datetime.timezone.utc)
                self.token=jsonData["access_token"]
                self.refreshToken=jsonData["refresh_token"]
            case TokenType.MCTOKEN:
                self.expireDate=datetime.datetime.fromisoformat(jsonData["result"]["validUntil"].replace("Z","+00:00"))
                self.token=jsonData["result"]["authorizationHeader"]
                self.refreshToken=None
            case TokenType.EDUTOKEN:
                self.expireDate=None
                self.token=jsonData["response"]
                self.refreshToken=None
            case TokenType.IMPORTED:
                self.expireDate=datetime.datetime.fromisoformat(jsonData["expires"].replace("Z","+00:00")) if jsonData["expires"] != None else None

                self.token=jsonData["token"]
                self.refreshToken=jsonData["refreshToken"]

                if jsonData["type"] == "MCTOKEN": self.type = TokenType.MCTOKEN
                if jsonData["type"] == "MSACCESS": self.type = TokenType.MSACCESS
                if jsonData["type"] == "EDUTOKEN": self.type = TokenType.EDUTOKEN

                if self.type == TokenType.IMPORTED: print("This token type is nonexistent. Somehow.")

    def fetchToken(self) -> str:
        if self.isExpired:
            self.refresh()
        return self.token

    def refresh(self) -> None:
        if self.type == TokenType.MSACCESS:
            self.processData(OAuth2Session(
                client_id="b36b1432-1a1c-4c82-9b76-24de1cab42f2",
                redirect_uri="https://login.microsoftonline.com/common/oauth2/nativeclient",
            ).refresh_token(
                token_url="https://login.microsoftonline.com/common/oauth2/token",
                refresh_token=self.refreshToken
            ))
        else:
            logger.warning("WARNING!!! Only MSTOKENS can be refreshed!")

    def export(self) -> dict:
        exportData={
            "type": self.type.name,
            "token": self.token,
            "refreshToken": self.refreshToken
        }
        
        exportData["expires"]=self.expireDate.isoformat() if self.expireDate!=None else self.expireDate
        return exportData

    @property
    def isExpired(self) -> bool: 
        return (self.expireDate < datetime.datetime.now(datetime.timezone.utc)) if (self.expireDate is not None) else False

class TokenProtocol(Protocol):
    "Token Protocol. I'll implement it in the next update!"
    def __init__(self,type,jsonData): ...
    def fetchToken(self): ...
    def refresh(self): ...
    def export(self): ...
    @property
    def isExpired(self): ...
