from strategy.hyperparams import ProviderHyperParamsStrategy
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider


class RealStatePositions:

    def __init__(self, provider_usdt_m, provider_coin_m):
        self.data_provider = BinanceDataProvider('', '', 'USDT-M')
        # self.provider_coin_m = BinanceDataProvider('', '', 'COIN-M')
        self.hyperparams_strategy = ProviderHyperParamsStrategy()

    def get_positions(self):
        tickers_usdtm = self.hyperparams_strategy.get_all_tickers(section='USDT-M')
        tickers_coinm = self.hyperparams_strategy.get_all_tickers(section='COIN-M')

        a = self.data_provider.get_amount_positions('ETHUSDT')
        b = self.data_provider.get_amount_positions('ETHUSD_PERP')

        print(a, b)







        return tickers_usdtm
