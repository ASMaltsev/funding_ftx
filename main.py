
from strategy.tools.funding_tools.data_provider_funding import DataProviderFunding
from strategy.tools.funding_tools.executor_funding import FundingExecutor
from strategy.tools.funding_tools.strategy_funding import StrateryFunding
from connectors import ConnectorRouter
import time

import logging
from my_logger import Logger

api_key = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
secret_key = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'

client = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector(api_key, secret_key)
data_provider = DataProviderFunding(client)
executor = FundingExecutor(client, data_provider)
stratery = StrateryFunding(data_provider, client)

while True:
    actions = stratery.decide()
    executor.execute(actions)
    time.sleep(10)
