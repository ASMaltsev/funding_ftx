from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.connetction_strategy_executor.translate_instructions import TranslateInstructions
from strategy.risk_control import Rebalancer


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def execute(self, instructions: dict, smoke=True):
        pass
    # array_actions = TranslateInstructions(data_provider_coin_m=self.data_provider_coin_m,
    #                                      data_provider_usdt_m=self.data_provider_usdt_m).parse(instructions)
    # print(array_actions)

    # print(Rebalancer(data_provider_usdt_m=self.data_provider_usdt_m,
    #                 data_provider_coin_m=self.data_provider_coin_m).analyze_account())

    def _union_instructions(self, strategy_instructions, rebalancer_instructions):
        pass
