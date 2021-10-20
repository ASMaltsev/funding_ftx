from connectors import ConnectorRouter
import datetime
from strategy.alpha.tools.abstract_tools import AbstractAlphaDataProvider


class DataProviderFunding(AbstractAlphaDataProvider):

    def __init__(self):
        self.connector_usdtm = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector()
        self.connector_coinm = ConnectorRouter(exchange='Binance', section='COIN-M').init_connector()

        self.PATH_API_PRICE_COINM = 'https://dapi.binance.com/dapi/v1/ticker/price?symbol='
        self.PATH_API_PRICE_USDTM = 'https://fapi.binance.com/fapi/v1/ticker/price?symbol='



    def get_price(self, ticker, section):
        if section == 'USDT-M':
            return float(requests.get(self.PATH_API_PRICE_USDTM+ticker).json()['price'])
        elif section == 'COIN-M':
            return float(requests.get(self.PATH_API_PRICE_COINM+ticker).json()[0]['price'])


    def get_tte(self, ticker_quart) -> int:
        tte = ticker_quart.split('_')[1]
        y = '20'+tte[:2]
        m = tte[2:4]
        d = tte[4:]
        date = f'{y}/{m}/{d}'
        date = datetime.datetime.strptime(date, "%Y/%m/%d")
        tte = (date - datetime.datetime.utcnow()).days
        return tte


    def get_spread(self, ticker_swap, ticker_quart, section):
        price_swap = self.get_price(ticker_swap, section)
        price_quart = self.get_price(ticker_quart, section)

        spread_pct = (price_quart - price_swap)/price_swap
        tte = self.get_tte(ticker_quart)
        spread_apr = spread_pct*365/tte

        return spread_pct, spread_apr
