"Methods for obtaining EDUTOKEN"
from .token import TokenType, Token
from ..config import get_config, BuildNumber, ProtocolVersion, DisplayVersion, VerifyHTTPS
from ..utils import uuid
import requests

def eduSignInV1(mstoken:Token) -> Token:
    signinData={
        "accessToken": mstoken.token,
        "build": BuildNumber,
        "clientVersion": ProtocolVersion,
        "correlationVector": get_config().vector,
        "displayVersion": DisplayVersion,
        "identityToken": mstoken.token,
        "locale": "en_US",
        "osVersion": "10.0.26100",
        "platform": "Windows Desktop Build (Win32)(x64)",
        "platformCategory": "desktop",
        "requestId": uuid()
    }
    signin=requests.post("https://login.minecrafteduservices.com/v2/signin",json=signinData,verify=False)
    signin.raise_for_status()
    eduToken=signin.json()
    return Token(TokenType.EDUTOKEN,eduToken)

def eduSignInV2(mstoken:Token) -> Token:
    ""
    config=get_config()
    reqid=uuid()
    head={"Connection": "Keep-Alive",
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json","User-Agent":"libhttpclient/1.0.0.0","api-version":"2.0",
    "Authorization":f"Bearer {mstoken.token}","request-id": reqid,"session-id": config.vector}
    signinData={
        "build": BuildNumber,
        "clientVersion": ProtocolVersion,
        "correlationVector": config.vector,
        # "delegationKey": generate_delegation_key(),
        "displayVersion": DisplayVersion,
        "locale": "en_US",
        "osVersion": "10.0.26100",
        "platform": "Windows Desktop Build (Win32)(x64)",
        "platformCategory": "desktop",
        "requestId": reqid
    }
    signin=requests.post("https://login.minecrafteduservices.com/signin",json=signinData,headers=head,verify=VerifyHTTPS)
    signin.raise_for_status()
    eduToken=signin.json()
    return Token(TokenType.EDUTOKEN,eduToken)

eduSignIn=eduSignInV2