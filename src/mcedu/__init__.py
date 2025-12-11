"Provides methods to query Minecraft Education's discovery API and to generate tokens."
from . import auth, config, discovery
from .auth import (
    PlayFabClient,
    mcSignin,
    eduSignIn,
    MSFTAuth,
    Token,
    TokenType,
    AuthFlow
)
from .config import (
    Config,
    get_config,
    GlobalLogger,
    setVersionData,
    BuildNumFromTrueVersion
)
from .discovery import (
    TokenCode,
    parseJoinCode,
    WorldParams,
    DiscoveryError,
    DiscoveryClient
)

def easyStartup():
    config=get_config()
    auth=config.authflow if ((config.loadSettings()) and (config.authflow is not None)) else AuthFlow()
    auth.importTokens(True)
    GlobalLogger.info("[Config] Imported Authentication Tokens")
    auth.requiredAuth()
    config.authflow=auth
    return auth

__all__=[
    "TokenCode",
    "parseJoinCode",
    "WorldParams",
    "DiscoveryError",
    "DiscoveryClient",
    "PlayFabClient",
    "mcSignin",
    "eduSignIn",
    "MSFTAuth",
    "Token",
    "TokenType",
    "AuthFlow",
    "GlobalLogger",
    "easyStartup",
    "BuildNumFromTrueVersion"
]