from strategy.tools.abstract_tools.abstract_executor import AbstractExecutor
from strategy.tools.abstract_tools.abstract_strategy import AbstractStrategy
from strategy.tools.funding_tools.data_provider_funding import DataProviderFunding
from connectors import ConnectorRouter
import time

import logging
from my_logger import Logger

class StrateryFunding(AbstractStrategy):
    """docstring for Strateryfunding."""

    def __init__(self, data_provider, client):
        self.data_provider = data_provider
        self.client = client

    def check_positions(self, client, ticker_swap, ticker_futures):
        pos_swap = client.get_positions(ticker_swap)[0]['positionAmt']
        pos_futures = client.get_positions(ticker_futures)[0]['positionAmt']
        print(pos_swap, pos_futures)

        return float(pos_swap), float(pos_futures)



    def decide(self):

        pos_swap, pos_futures = self.check_positions(self.client, 'ETHUSDT', 'ETHUSDT_211231')

        if pos_swap == pos_futures == 0:
            actions  = {
                            'ETHUSDT': -0.03,
                            'ETHUSDT_211231': 0.03
                        }
        else:
            actions  = {
                            'ETHUSDT': 0.03,
                            'ETHUSDT_211231': -0.03
                        }

        return actions
