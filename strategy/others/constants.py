import os

API_KEY = os.getenv('api_key', '')
SECRET_KEY = os.getenv('secret_key', '')


STATHAM_TOKEN = os.getenv('statham_token', '')
STATHAM_CHAT_ID = os.getenv('statham_chat_id', 0)
LABEL = os.getenv('label', '')
SECTION = os.getenv('section', '')

# logging
HOSTS = os.getenv('hosts', '')
USER_NAME = os.getenv('user_name', '')
USER_PASS = os.getenv('user_pass', '')
