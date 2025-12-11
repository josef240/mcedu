"Methods for obtaining Microsoft Entra Credentials (for Minecraft Education specifically)"
from requests_oauthlib import OAuth2Session
from .token import TokenType, Token

class MSFTAuth():
    "Simple class to obtain Microsoft Entra credentials for MCEDU"
    def createMSAuthLink(self):
        """Creates a Microsoft Authorization Link.
        Returns:
           str: Microsoft Authorization URL"""
        # Please use Device Code Authorization Flow: 10x better than this.
        oauth = OAuth2Session(
                client_id="b36b1432-1a1c-4c82-9b76-24de1cab42f2",
                redirect_uri="https://login.microsoftonline.com/common/oauth2/nativeclient",
            )

        authorization_url, state = oauth.authorization_url(
                url="https://login.microsoftonline.com/common/oauth2/authorize",
                resource="https://meeservices.minecraft.net",
                
            )
        self.oauth=oauth
        self.authlink=authorization_url
        return authorization_url

    def processMSAuthLink(self,clientLink:str):
        token = self.oauth.fetch_token(
            token_url="https://login.microsoftonline.com/common/oauth2/token",
            authorization_response=clientLink,
            include_client_id=True,
        )
        self.token=token
        return Token(TokenType.MSACCESS,token)
