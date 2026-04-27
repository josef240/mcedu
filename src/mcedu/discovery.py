"Provides methods to query Minecraft Education's discovery API."
from .config import BuildNumber, VerifyHTTPS
from typing import Optional, TypeAlias, Literal
from dataclasses import dataclass
from .auth.token import Token
import itertools
import requests
import logging
import base64

logger = logging.getLogger("mcedu.discovery")
logger.setLevel(logging.INFO)

#There maybe more symbols than 18, but I don't know them. Luckily the order of symbols is the same!
codeSymbols=["Book","Balloon","Rail","Alex","Cookie","Fish","Agent","Cake","Pickaxe", "WaterBucket", "Steve", "Apple","Carrot","Panda","Sign","Potion","Map","Llama"]
"This is a list of join code symbols. If more than 18 exist, sent me a screenshot of your join world screen."

TokenCode: TypeAlias = tuple[str,str]
"The first string has a server token, the second has an unparsed join code."

def parseJoinCode(passcode:str) -> str:
    "Simple function to turn unparsed join codes into something human readable. If it fails it returns an empty string."
    global codeSymbols
    items=passcode.split(",")
    symbolList=[]
    for item in items:
        if item.isdigit: symbolNum=int(item)
        else: return

        if len(codeSymbols)>symbolNum>-1: symbol=codeSymbols[symbolNum]
        else: 
            logger.error(f"Could not parse joincode: {passcode}")
            raise DiscoveryError(f"Could not parse joincode: {passcode}")
        symbolList.append(symbol)

    return ", ".join(symbolList)

def encodeJoinCode(passcode:str) -> str:
    global codeSymbols
    upperSymbols=[s.upper() for s in codeSymbols]
    items=passcode.upper().replace(" ","").split(",")
    symbolList=[str(upperSymbols.index(item)) for item in items]
    return ",".join(symbolList)

@dataclass
class WorldParams():
    """Holds simple information about a Minecraft world like it's name, host, and nethernetID. (If avaliable).
    \nThe value of name & details can be any string and the maxPlayers & playerCount can be any positive number or zero."""
    # The value of name/details can be anything
    name:str="New World"
    details:str="SmithJ"
    maxPlayers:int=8
    playerCount:int=1
    nethernetID:str=None    

class DiscoveryError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class DiscoveryClient():
    """A simple client for interacting with MCEDU's discovery system. Incompatible with versions of MCEDU older than 1.21.90.
    
    Args:
        mstoken (Token): The Microsoft Token to use for authentication.
    """
    __client_id = itertools.count()
    def __init__(self, mstoken:Token) -> None:
        self.headers={
            "Authorization": f"Bearer {mstoken.token}",
            "api-version":"2.0",
            "Connection": "Keep-Alive",
            "Content-Type": "application/json",
            "User-Agent":"libhttpclient/1.0.0.0"
        }
        self.__session=requests.Session()
        self.mstoken=mstoken
        self.__hosting=False
        self.__id=next(self.__client_id)
        self.world:Optional[WorldParams]=None
        self.__session.headers=self.headers.copy()
        self.__session.verify=VerifyHTTPS
        self.v2=True

    def host(self, world:WorldParams) -> Optional[TokenCode]:
        """Hosts a world on Discovery.
        
        Note: 
            You cannot host two worlds on the same DiscoveryClient.
        
        Args:
            world (WorldParams): The data of the world you want to host.

        Returns:
            Optional[TokenCode]: An unparsed join code & a server token, or None if it fails.

        Raises:
            DiscoveryError: If the request fails.
        """
        if self.__hosting:
            return
        
        self.world=world
        hostData={
            "build": BuildNumber,
            "locale": "en_US",
            "maxPlayers": world.maxPlayers,
            "networkId": str(world.nethernetID),
            "playerCount": world.playerCount,
            "protocolVersion": 1,
            "serverDetails": world.details,
            "serverName": world.name,
            "transportType": 2
        }
        hostResponse=self.__request("host",payload=hostData)
        self.serverToken:str=hostResponse["serverToken"]
        self.passcode:str=hostResponse["passcode"]
        self.__session.headers["Authorization"]= f"Bearer {self.serverToken}"
        self.__hosting=True
        return (self.serverToken,self.passcode)

    def dehost(self) -> None:
        """Only runs if you're hosting, and delists your world from discovery, destroying the joincode.
        \nMake sure to do this for every world after you're done with it, or else the Discovery API won't work with you for a bit."""
        if not self.__hosting:
            return
        dehostData={
            "build": BuildNumber,
            "locale": "en_US",
            "passcode": self.passcode,
            "protocolVersion": 1,
        }
        self.__request("dehost",payload=dehostData,silentExpected=True)
        self.__hosting=False
        return
    
    def reloadJoinCode(self) -> Optional[TokenCode]:
        "This uses the ingame method of changing the join code: Dehost & Rehost."
        self.dehost()
        return self.host(self.world)

    def heartbeat(self) -> None:
        """Execute this function every 100 seconds after the world is listed in Discovery for the world to stay there.
        \nDon't do heartbeats if you didn't start hosting a world."""
        if not self.__hosting:
            return
        heartbeatData={
            "build": BuildNumber,
            "locale": "en_US",
            "passcode": self.passcode,
            "protocolVersion": 1,
            "transportType":2
        }
        heartbeat=self.__request("heartbeat",payload=heartbeatData,silentExpected=True)
        return
        
    def update(self,updatedWorld:Optional[WorldParams]=None) -> Optional[TokenCode]:
        """Use this to update world data on Discovery. It returns an unparsed join code & a server token.
        \nYou cannot update a world if you are not hosting."""
        if not self.__hosting:
            return
        world=updatedWorld if ((updatedWorld!=self.world) and (updatedWorld)) else self.world
        hostData={
            "build": BuildNumber,
            "locale": "en_US",
            "maxPlayers": world.maxPlayers,
            "passcode": self.passcode,
            "playerCount": world.playerCount,
            "protocolVersion": 1,
            "serverDetails": world.details,
            "serverName": world.name,
        }
        self.world=world
        self.__request("update",payload=hostData,silentExpected=True)
        self.__hosting=True
        return (self.serverToken,self.passcode)
    
    def query(self,passcode:str) -> Optional[WorldParams]:
        """This looks for worlds in your tenant that are on Discovery. 
It will return worlds on different builds than the one you specify. Returns WorldParams if successful, or None if not.
\nThis will fail if you are hosting a world and query with the same DiscoveryClient. """
        if self.__hosting:
            return
        
        queryData={
            "build": BuildNumber,
            "locale": "en_US",
            "passcode": passcode,
            "protocolVersion": 1
        }
        query=self.__request("joininfo",payload=queryData)
        if query is None: return
        connectionID=str(query["connectionInfo"]["info"]["id"])
        extWorld=WorldParams(query["serverName"],query["serverDetails"],nethernetID=connectionID)
        return extWorld
    
    def clean(self):
        "Clean slate. Resets all variables to their original values."
        if self.__hosting:
            self.dehost()
        self.__session.headers=self.headers.copy()
        self.serverToken=self.passcode=""
        self.world=None

    def __str__(self):
        return f"DiscoveryClient({self.__id})"

    def __repr__(self):
        return f"DiscoveryClient(id={self.__id}, hosting={self.__hosting})"

    @property
    def state(self) -> Literal["invalid","inactive","active"]:
        return "invalid" if self.mstoken.isExpired else ("active" if self.__hosting else "inactive")

    @property
    def joinlink(self) -> str:
        "Creates a link using your joincode. The link redirects to MCEDU and types in a joincode."
        if not self.__hosting:
            logger.error("Failed to generate joinlink: DiscoveryClient not hosting.")
            raise DiscoveryError("Failed to generate joinlink: DiscoveryClient not hosting.")
        if (self.passcode == None):
            logger.error("Failed to generate joinlink: Joincode is None")
            raise DiscoveryError("Failed to generate joinlink: Joincode is None")
            
        jlink="https://education.minecraft.net/joinworld/"
        jlink+=base64.b64encode(self.passcode)
        return jlink

    @property
    def isHosting(self) -> bool:
        "Returns whether this client is hosting on Discovery"
        return self.__hosting

    def __request(self, endpoint:str,payload:dict,silentExpected=False):
        "Internal method to send requests to MCEDU Discovery API"
        url="https://discovery.minecrafteduservices.com/"+endpoint
        try:
            query=self.__session.post(url,json=payload)
            query.raise_for_status()
        except Exception as e:
            if hasattr(query,"status_code") and (query.status_code==404): return
            logger.error(f"DiscoveryClient Request to {endpoint} failed")
            logger.debug(f"Endpoint:{endpoint};Payload:{payload};silentExpected:{silentExpected};Exception Args:{e.args}")
            if endpoint!="dehost":self.dehost()
            raise DiscoveryError(e.args)
        
        #Some logic to check if we got a silent response when we wanted one
        silent = (query.content == b"")

        if silent == silentExpected:
            return query.json() if not silent else {}

        if endpoint!="dehost":self.dehost()
        error_msg = f"Silent return expected, received response from {url}: {query.content}" if silentExpected \
                    else f"Silent return not expected, received response from {url}"
        raise DiscoveryError(error_msg)

__all__=[
    "codeSymbols"
    "TokenCode"
    "parseJoinCode",
    "encodeJoinCode",
    "WorldParams",
    "DiscoveryError",
    "DiscoveryClient"
]