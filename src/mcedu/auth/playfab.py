"Methods for accessing Minecraft Education's Playfab API"
from ..config import VerifyHTTPS, get_config
from ..utils import generatePlayfabID
from typing import Dict, Optional, Any, TypeAlias
import logging
import requests
import os

# I did not write this Playfab code, only picked it up and modified it from https://github.com/DJStompZone/PyNetherNet. I 
# understand how it works however, and this is not a significant portion of his code, so I didn't include his license file.

PlayfabRequestPayload: TypeAlias = dict[str, None | bool | dict[str, bool] | str]
logger=logging.getLogger("mcedu.auth.playfab")

class PlayFabClient:
    """
    A client for interacting with the PlayFab API. This code is from https://github.com/DJStompZone/PyNetherNet. I did not write this.
    But again, I think this is stolen from the Pillager's Bay EzTestcoin 0.2, so...
    """

    TITLE_ID = "6955F"

    def __init__(self) -> None:
        """
        Initializes the PlayFabClient instance, setting up the session and loading settings.
        """
        self.req = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "libhttpclient/1.0.0.0",
            "Content-Type": "application/json",
            "Accept-Language": "en-US"
        })
        self.domain = f"https://{self.TITLE_ID.lower()}.playfabapi.com"

    def send_playfab_request(self,
                             endpoint: str,
                             data: PlayfabRequestPayload,
                             headers: Optional[Dict[str, str]] = None
                             ) -> PlayfabRequestPayload:
        """
        Sends a request to the PlayFab API.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (PlayfabRequestPayload): The payload to send in the request.
            headers (Optional[Dict[str, str]]): Optional headers to include in the request.

        Returns:
            PlayfabRequestPayload: The response data from the API.
        """
        try:
            rsp = self.session.post(self.domain + endpoint, json=data, headers=headers,verify=VerifyHTTPS)
            rsp.raise_for_status()
            return rsp.json()['data']
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            logger.debug(f"Failed request payload: {e.request.body}")
            logger.debug(f"Failed response content: {e.response.content}")
            return {}

    def login_with_custom_id(self, custom_id="") -> Optional[Dict[str, Any]]:
        """
        Logs in a user with a custom ID, creating a new account if necessary.

        Returns:
            dict: The response data from the login request.
        """
        create_new_account = False

        if custom_id == "":
            custom_id = generatePlayfabID()
            get_config().playfabid=custom_id
            create_new_account = True


        payload: PlayfabRequestPayload = {
            "CreateAccount": None,
            "CustomId": None,
            "EncryptedRequest": None,
            "InfoRequestParameters": {
                "GetCharacterInventories": False,
                "GetCharacterList": False,
                "GetPlayerProfile": True,
                "GetPlayerStatistics": False,
                "GetTitleData": False,
                "GetUserAccountInfo": True,
                "GetUserData": False,
                "GetUserInventory": False,
                "GetUserReadOnlyData": False,
                "GetUserVirtualCurrency": False,
                "PlayerStatisticNames": None,
                "ProfileConstraints": None,
                "TitleDataKeys": None,
                "UserDataKeys": None,
                "UserReadOnlyDataKeys": None
            },
            "PlayerSecret": None,
            "TitleId": self.TITLE_ID
        }
        self.req = None

        payload["CreateAccount"] = True if create_new_account else None
        payload["CustomId"] = custom_id
        self.req = self.send_playfab_request("/Client/LoginWithCustomID", payload)
        return self.req
