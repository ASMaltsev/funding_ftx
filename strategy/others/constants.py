import os
import json
import boto3
import base64
from botocore.exceptions import ClientError

LABEL = os.getenv('label', 'TEST')


STATHAM_TOKEN = os.getenv('statham_token', '2118072648:AAGqx1UQnzH-amupBMfGagwrwSeGTvec4jk')
STATHAM_CHAT_ID = os.getenv('statham_chat_id', -609260691)

SECTION = os.getenv('section', 'BTC')

# logging
HOSTS = os.getenv('hosts', '18.179.17.136')

API_KEY = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
SECRET_KEY = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'
ELASTIC_NAME = os.getenv('elastic_name', 'elastic')
ELASTIC_PASS = os.getenv('elastic_pass', 'XxLdubKyIczagFHBh8Va')

HOST_DB = os.getenv('host_db', '52.198.147.90')
USER_NAME = os.getenv('user_name', 'super_user')
USER_PASS = os.getenv('user_pass', '76gCTR76sg15d')
