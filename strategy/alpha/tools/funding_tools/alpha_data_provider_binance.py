from connectors import ConnectorRouter
import datetime
from strategy.alpha.tools.abstract_tools.abstract_data_provider import AbstractAlphaDataProvider


class DataProviderFunding(AbstractAlphaDataProvider):

    def __init__(self):
        self.connector_usdtm = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector()
        self.connector_coinm = ConnectorRouter(exchange='Binance', section='COIN-M').init_connector()

    def get_price(self, ticker):
        section = 'USDT-M' if ticker.split('_')[0][-1] == 'T' else 'COIN-M'
        connector = self.connector_usdtm if section == 'USDT-M' else self.connector_coinm
        bbid_bask = connector.get_bbid_bask(ticker)
        bbid = float(bbid_bask['bidPrice'])
        bask = float(bbid_bask['askPrice'])
        mid_price = (bbid + bask) / 2
        return mid_price

    def get_tte(self, ticker_quart) -> int:
        tte = ticker_quart.split('_')[1]
        y = '20' + tte[:2]
        m = tte[2:4]
        d = tte[4:]
        date = f'{y}/{m}/{d}'
        date = datetime.datetime.strptime(date, "%Y/%m/%d")
        tte = (date - datetime.datetime.utcnow()).days
        return tte

    def get_spread(self, ticker_swap, ticker_quart):
        price_swap = self.get_price(ticker_swap)
        price_quart = self.get_price(ticker_quart)

        spread_pct = (price_quart - price_swap) / price_swap
        tte = self.get_tte(ticker_quart)
        spread_apr = spread_pct * 365 / tte

        return spread_pct, spread_apr
