from connectors import ConnectorRouter

from strategy.alpha.tools.abstract_tools import AbstractAlphaDataProvider


class DataProviderFunding(AbstractAlphaDataProvider):

    def __init__(self, section):
        self.connection = ConnectorRouter(exchange='Binance', section=section).init_connector()

    def get_bbid_bask(self, ticker: str):
        response = self.connection.get_bbid_bask(ticker=ticker)
        return response['bidPrice'], response['askPrice']
