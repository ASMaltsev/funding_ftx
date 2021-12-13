import os
import json
import boto3
import base64
from botocore.exceptions import ClientError

secret_name = os.getenv('secret_name')


def get_secret(name_key):
    global secret_name
    region_name = "ap-northeast-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        key = get_secret_value_response["SecretString"]
        data = json.loads(key)
        for item in data:
            if data[item]['label'] == name_key:
                api_key = data[item]['api_key']
                api_secret = data[item]['api_secret']
        return api_key, api_secret
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])


API_KEY = get_secret('api_key')
SECRET_KEY = get_secret('secret_key')

STATHAM_TOKEN = get_secret('statham_token')
STATHAM_CHAT_ID = get_secret('statham_chat_id')

LABEL = os.getenv('label')
SECTION = os.getenv('section')

# logging
HOSTS = os.getenv('hosts')

ELASTIC_NAME = os.getenv('elastic_name')
ELASTIC_PASS = os.getenv('elastic_pass')

HOST_DB = os.getenv('host_db')
USER_NAME = os.getenv('user_name')
USER_PASS = os.getenv('user_pass')
