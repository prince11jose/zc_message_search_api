import requests
import time
import logging
from config import load_config

logger = logging.getLogger(__name__)

class ZohoCliqAPI:
    def __init__(self):
        config = load_config()
        self.company_id = config["zoho"]["company_id"]
        self.client_id = config["zoho"]["client_id"]
        self.client_secret = config["zoho"]["client_secret"]
        self.auth_code = config["zoho"]["auth_code"]
        self.refresh_token = config["zoho"].get("refresh_token", None)
        self.access_token = None
        self.token_expiry = None
        self.censor_api_endpoint = config["censor_api"]["endpoint"]

    def get_access_token(self):
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            logger.info("Using cached access token")
            return self.access_token

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code" if not self.refresh_token else "refresh_token"
        }
        if self.refresh_token:
            params["refresh_token"] = self.refresh_token
        else:
            params["code"] = self.auth_code

        logger.info("Requesting access token")
        logger.debug(f"Request parameters: {params}")

        token_url = "https://accounts.zoho.com/oauth/v2/token"
        response = requests.post(token_url, data=params)
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        if "access_token" in response_data:
            self.access_token = response_data["access_token"]
            self.token_expiry = time.time() + response_data.get("expires_in", 3600)
            if "refresh_token" in response_data:
                self.refresh_token = response_data["refresh_token"]
                self.update_refresh_token(self.refresh_token)
            logger.info("Access token obtained successfully")
            return self.access_token
        else:
            logger.error(f"Failed to get access token: {response_data}")
            raise Exception(f"Failed to get access token: {response_data}")

    def update_refresh_token(self, refresh_token):
        logger.info("Updating refresh token in config.ini")
        config_path = "config.ini"
        config = load_config()
        config["zoho"]["refresh_token"] = refresh_token
        with open(config_path, "w") as configfile:
            config.write(configfile)

    def search_messages(self, query):
        access_token = self.get_access_token()
        search_url = f"https://cliq.zoho.com/company/{self.company_id}/adminapi/v1/messagesearch?message={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Authorization": f"Zoho-oauthtoken {access_token}"
        }

        logger.info(f"Searching messages with query: {query}")
        response = requests.get(search_url, headers=headers)
        logger.debug(f"Response status: {response.status_code}, Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Refresh token and retry once if token expired
            logger.warning("Access token expired, refreshing token")
            self.access_token = None
            access_token = self.get_access_token()
            headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
            response = requests.get(search_url, headers=headers)
            logger.debug(f"Retry response status: {response.status_code}, Response: {response.text}")
            if response.status_code == 200:
                return response.json()

        logger.error(f"Failed to search messages, status code: {response.status_code}")
        response.raise_for_status()

    def analyze_text(self, text):
        detect_url = self.censor_api_endpoint
        headers = {"Content-Type": "application/json"}
        data = {"text": text}

        logger.info("Analyzing text for credentials")
        response = requests.post(detect_url, headers=headers, json=data)
        logger.debug(f"Analysis response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to analyze text, status code: {response.status_code}")
            response.raise_for_status()

    def post_message(self, chid):
        access_token = self.get_access_token()
        post_url = f"https://cliq.zoho.com/api/v2/chats/{chid}/message"
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        data = {
                        "text": "Please remember not to share any sensitive information during this conversation to ensure your data stays safe.",
                        "bot": {
                            "name": "Credential Censor Bot",
                            "image": "https://www.zoho.com/cliq/help/restapi/images/bot-custom.png"
                        },
                        "card": {
                            "theme": "modern-inline"
                        },
                        "slides": [
                            {
                                "type": "list",
                                "title": "Security Reminder",
                                "data": [
                                    "Avoid sharing personal identification numbers (PINs)",
                                    "Do not disclose passwords",
                                    "Refrain from sharing any confidential business details",
                                    "Be cautious about providing sensitive customer information"
                                ]
                            }
                        ]
                    }

        logger.info(f"Posting message to chid: {chid}")
        response = requests.post(post_url, headers=headers, json=data)
        logger.debug(f"Post response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to post message, status code: {response.status_code}")
            response.raise_for_status()
