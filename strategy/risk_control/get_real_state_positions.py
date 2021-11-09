from strategy.hyperparams import ProviderHyperParamsStrategy


class RealStatePositions:

    def __init__(self, data_provider_usdt_m, data_provider_coin_m):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.hyperparams_strategy = ProviderHyperParamsStrategy()

    def get_positions(self):
        tickers_pos_quart = {}
        tickers_pos_perp = {}
        tickers_usdt_m = self.hyperparams_strategy.get_list_tickers(section='USDT-M', kind='quart')

        tickers_coin_m = self.hyperparams_strategy.get_list_tickers(section='COIN-M', kind='current') + \
                         self.hyperparams_strategy.get_list_tickers(section='COIN-M', kind='next')

        for ticker_usdt in tickers_usdt_m:
            tickers_pos_quart[ticker_usdt] = self.data_provider_usdt_m.get_amount_positions(ticker_usdt)
        for ticker_coin in tickers_coin_m:
            tickers_pos_quart[ticker_coin] = self.data_provider_coin_m.get_amount_positions(ticker_coin)

        tickers_usdt_m_perp = self.hyperparams_strategy.get_list_tickers(section='USDT-M', kind='perp')
        tickers_coin_m_perp = self.hyperparams_strategy.get_list_tickers(section='COIN-M', kind='perp')

        for ticker_usdt in tickers_usdt_m_perp:
            tickers_pos_perp[ticker_usdt] = self.data_provider_usdt_m.get_amount_positions(ticker_usdt)
        for ticker_coin in tickers_coin_m_perp:
            tickers_pos_perp[ticker_coin] = self.data_provider_coin_m.get_amount_positions(ticker_coin)

        return tickers_pos_quart, tickers_pos_perp
