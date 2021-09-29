import sys
sys.path.insert(1, '../abstract_tools/')

from abstract_data_provider import AbstractDataProvider
from connectors import ConnectorRouter

class DataProviderFunding(AbstractDataProvider):
    """DataProviderFunding"""

    def __init__(self, client):
        self.client = client

    def get_orderbook(self, ticker: str, limits: int):
        return self.client.get_orderbook(ticker, limits)

    def get_positions(self, ticker: str):
        return self.client.get_positions(ticker)

    def get_bbid_bask(self, ticker: str):
        return self.client.get_bbid_bask(ticker)

    def status_order(self, ticker: str, order_id: int):
        return self.client.status_order(ticker, order_id)
