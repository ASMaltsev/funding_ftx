from strategy.hyperparams import ProviderHyperParamsStrategy


class RealStatePositions:

    def __init__(self, provider_usdt_m, provider_coin_m):
        self.provider_usdt_m = provider_usdt_m
        self.provider_coin_m = provider_coin_m
        self.hyperparams_strategy = ProviderHyperParamsStrategy()

    def get_positions(self):
        self.hyperparams_strategy.get_all_tickers(section='USDT-M')