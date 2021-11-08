from strategy.hyperparams import ProviderHyperParamsStrategy


class RealStatePositions:

    def __init__(self, data_provider_usdt_m, data_provider_coin_m):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.hyperparams_strategy = ProviderHyperParamsStrategy()

    def get_positions(self):
        tickers_pos = {}
        tickers_usdt_m = self.hyperparams_strategy.get_list_tickers(section='USDT-M', kind='quart')
        tickers_coin_m = self.hyperparams_strategy.get_list_tickers(section='COIN-M', kind='current') + \
                         self.hyperparams_strategy.get_list_tickers(section='COIN-M', kind='next')
        for ticker_usd in tickers_usdt_m:
            tickers_pos[ticker_usd] = self.data_provider_usdt_m.get_amount_positions(ticker_usd)
        for ticker_coin in tickers_coin_m:
            tickers_pos[ticker_coin] = self.data_provider_coin_m.get_amount_positions(ticker_coin)
        return tickers_pos
