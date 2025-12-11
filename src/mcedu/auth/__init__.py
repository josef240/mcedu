"Provides methods to get & refresh tokens related to Minecraft Education"
from .token import TokenType, Token
from .playfab import PlayFabClient
from .minecraft import mcSignin
from ..config import get_config
from .edutoken import eduSignIn
from .msft import MSFTAuth
from typing import Tuple
import webbrowser
import json
import re

class AuthFlow():
    "Easy to use class that contains several flows for authentication"
    def __init__(self) -> None:
        self.mctokenValid=False
        self.mstokenValid=False
        self.edutokenValid=False

    def MSAccessAuth(self) -> Token:
        msftmanager=MSFTAuth()
        webbrowser.open(msftmanager.createMSAuthLink())
        while True:
            authorization_response = re.search("https://login.microsoftonline.com/common/oauth2/nativeclient[^ ]+", input("Sign in with your work/school account, then paste the link it redirects you to here: ")).group(0)

            if ".." in authorization_response:
                print("You have provided a shortened response. Try right clicking the message box and choosing 'copy full text' ")
                continue

            break
        mstoken=msftmanager.processMSAuthLink(authorization_response)
        self.mstokenValid=True
        self.mstoken=mstoken
        return mstoken
    
    def MCTokenAuth(self,playfabid="",deviceid="") -> Token:
        c=get_config()
        if (playfabid==None) or (deviceid == None): raise Exception("PlayfabID or DeviceID is null")
        mctoken=mcSignin(playfabid, deviceid)
        self.mctokenValid=True
        self.mctoken=mctoken
        return mctoken

    def EduTokenAuth(self,mstoken) -> Token:
        edutoken=eduSignIn(mstoken)
        self.edutokenValid=True
        self.edutoken=edutoken
        return edutoken

    def requiredAuth(self,playfabid="",deviceid=""):
        "Only does authentication for values that aren't already set."

        if not self.mstokenValid: mstoken=self.MSAccessAuth()

        if not self.mctokenValid: mctoken=self.MCTokenAuth(playfabid,deviceid)

        if not self.edutokenValid: edutoken=self.EduTokenAuth(mstoken)

        return

    def fullAuth(self,playfabid="",deviceid="") -> Tuple[Token,Token,Token]:
        """Does all the authentication Minecraft Education needs.
        Returns:
            Tuple[Token,Token,Token]: MCToken, Microsoft Entra Credentials, EDUTOKEN"""
        mstoken=self.MSAccessAuth()

        mctoken=self.MCTokenAuth(playfabid,deviceid)

        edutoken=self.EduTokenAuth(mstoken)

        return mctoken, mstoken, edutoken

    def __str__(self) -> str:
        variables=[
            f"mstoken={self.mstoken}" if self.mstokenValid else "",
            f"mctoken={self.mctoken}" if self.mctokenValid else "",
            f"edutoken={self.edutoken}"if self.edutokenValid else "",
        ]
        string="Authflow["
        string+=(",".join(variables))
        string+="]"
        return string

    def exportTokens(self,write=True) -> dict:
        tokens=[]
        if self.mctokenValid:
            tokens.append(self.mctoken.export())
        if self.mstokenValid:
            tokens.append(self.mstoken.export())
        if self.edutokenValid:
            tokens.append(self.edutoken.export())
        
        if write:
            with open("tokens.json","w") as file:
                json.dump(obj={"tokens":tokens},fp=file,indent=4)


        return {"tokens":tokens}

    def importTokens(self,read=True) -> None:
        if read:
            try:
                with open("settings.json","r") as file:
                    data:dict=json.load(file)
            except Exception as e:
                return
            
        if not ("tokens" in data.keys()):
            return
        
        for item in data["tokens"]:
            if item["type"]=="MCTOKEN":
                self.mctoken=Token(TokenType.IMPORTED,item)
                self.mctokenValid=(not self.mctoken.isExpired)
                if not self.mctokenValid: self.MCTokenAuth()
            if item["type"]=="MSACCESS":
                self.mstoken=Token(TokenType.IMPORTED,item)
                if self.mstoken.isExpired:
                    self.mstoken.refresh()
                self.mstokenValid=True
            if item["type"]=="EDUTOKEN":
                self.edutoken=Token(TokenType.IMPORTED,item)
                self.edutokenValid=True
