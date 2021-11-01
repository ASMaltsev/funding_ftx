from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.connetction_strategy_executor.translate_instructions import TranslateInstructions
from strategy.risk_control import Rebalancer


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
        self.data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')

    def execute(self, instructions: dict, smoke=True):
        # array_actions = TranslateInstructions(data_provider_coin_m=self.data_provider_coin_m,
        #                                      data_provider_usdt_m=self.data_provider_usdt_m).parse(instructions)
        # print(array_actions)

        print(Rebalancer(data_provider_usdt_m=self.data_provider_usdt_m,
                         data_provider_coin_m=self.data_provider_coin_m).analyze_account())

    def _union_instructions(self, strategy_instructions, rebalancer_instructions):
        pass
