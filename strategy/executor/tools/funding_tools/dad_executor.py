from strategy.executor.tools.funding_tools.binance_data_provider import BinanceDataProvider
from strategy.executor.tools.funding_tools.translate_instructions import TranslateInstructions


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
        self.data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')

    def execute(self, instructions: dict, smoke=True):
        if not smoke:
            array_actions = TranslateInstructions(data_provider_coin_m=self.data_provider_coin_m,
                                                  data_provider_usdt_m=self.data_provider_usdt_m).parse(instructions)
            print(array_actions[1])
