from strategy.hyperparams import ProviderHyperParamsStrategy
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider


class RealStatePositions:

    def __init__(self, api_key, secret_key):
        self.data_provider_usdtm = BinanceDataProvider(api_key, secret_key, 'USDT-M')
        self.data_provider_coinm = BinanceDataProvider(api_key, secret_key, 'COIN-M')
        self.hyperparams_strategy = ProviderHyperParamsStrategy()

    def get_positions(self):
        tickers_pos = {}
        tickers_usdtm = self.hyperparams_strategy.get_all_tickers(section='USDT-M')
        tickers_coinm = self.hyperparams_strategy.get_all_tickers(section='COIN-M')

        for ticker_usd in tickers_usdtm:
            tickers_pos[ticker_usd] = self.data_provider_usdtm.get_amount_positions(ticker_usd)
        for ticker_coin in tickers_coinm:
            tickers_pos[ticker_coin] = self.data_provider_coinm.get_amount_positions(ticker_coin)


        return tickers_pos
