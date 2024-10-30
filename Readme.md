# Zoho Cliq Message Search and [Credential Censor API] (https://github.com/prince11jose/credential_censor_api)

This project provides an API for searching messages in Zoho Cliq, analyzing them for sensitive credentials, and optionally censoring them by posting to specific channels. It includes features for obtaining access tokens using OAuth and securely managing Zoho API credentials.

## Features

* Search messages in Zoho Cliq using keywords.
* Analyze message content for sensitive information.
* Automatically post a response to a chat if sensitive content is detected.
* OAuth integration for Zoho Cliq with support for refresh tokens.

## Requirements

Python 3.8+
Zoho Developer account

## Setup Instructions

### Step 1: Clone the Repository
```
git clone https://github.com/prince11jose/zc_message_search_api.git
cd zc_message_search_api
```
### Step 2: Create a Virtual Environment

Create and activate a virtual environment to keep dependencies isolated.
```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

Install the required dependencies from requirements.txt:
```
pip install -r requirements.txt
```

### Step 4: Configure Settings

Update the configuration file (config.ini) with your Zoho API credentials and the censor API endpoint:
```
[zoho]
company_id = YOUR_COMPANY_ID
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
auth_code = YOUR_AUTH_CODE
refresh_token = YOUR_REFRESH_TOKEN

[censor_api]
endpoint = http://localhost:8000/detect_credentials
```
Credential Censor API needs to be hosed before the Zoho Cliq Message Search API is hosted.

* company_id: Your Zoho Cliq company ID.
* client_id: Client ID from Zoho API console.
* client_secret: Client Secret from Zoho API console.
* auth_code: Authorization code obtained from Zoho.
* refresh_token: Refresh token for obtaining new access tokens.

### Step 5: Run the Flask Application

Start the Flask API server:
```
python app.py
```

## API Endpoints

1. /search_and_post
Method: POST
Description: Searches messages in Zoho Cliq for specified keywords and analyzes them for credentials.
Request Body:
```
{
  "search_query": "username,password,pwd,pass"
}
```

### Example Usage

You can use curl to interact with the /search_and_post endpoint:
```
curl --location --request POST 'http://127.0.0.1:5000/search_and_post' \
--header 'Content-Type: application/json' \
--data-raw '{"search_query": "username,password,pwd,pass"}'
```

## Logging

Logging is configured to provide detailed information on the application's activities. Logs are written to both the console and a file named app.log.
* Log Levels: The default logging level is set to INFO. You can change this in config.py by modifying the level parameter in the setup_logging() function.

## Notes on Zoho OAuth

Authorization Code: The authorization code must be used immediately after obtaining it, as it expires quickly and can only be used once.
Refresh Tokens: The script is configured to store and reuse refresh tokens, which simplifies obtaining access tokens without needing a new authorization code each time.

## Troubleshooting

 ### invalid_code Error

If you see an invalid_code error, the authorization code has likely expired or been used already. Generate a new authorization code and update config.ini accordingly.

## Project Structure
```
project/
├── app.py                    # Main Flask application
├── api.py                     # ZohoCliqAPI class for interacting with Zoho Cliq APIs
├── config.py                # Configuration and logging setup
├── config.ini                # Configuration file for storing credentials
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.