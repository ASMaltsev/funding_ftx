import os

API_KEY = os.getenv('api_key', '')
SECRET_KEY = os.getenv('secret_key', '')


STATHAM_TOKEN = os.getenv('statham_token', '')
STATHAM_CHAT_ID = os.getenv('statham_chat_id', 0)
CLIENT_NAME = os.getenv('client_name', '')
SECTION = os.getenv('section', '')

# logging
HOSTS = os.getenv('hosts', '')
USER_NAME = os.getenv('db_name', '')
USER_PASS = os.getenv('db_pass', '')
