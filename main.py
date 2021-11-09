from strategy.executor import DadExecutor
from strategy.logging import Logger

api_key = ''
secret_key = ''
logger = Logger('Main').create()

try:
    DadExecutor(api_key=api_key, secret_key=secret_key).execute()
except Exception as e:
    logger.error(e)
