import math
from strategy.translation import GeneratePosition
from strategy.hyperparams import ProviderHyperParamsStrategy


class TranslateLeverage:

    def __init__(self, data_provider_usdt_m, data_provider_coin_m):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.generate_position = GeneratePosition()
        self.hyperparams_provider = ProviderHyperParamsStrategy()

    def translate(self, instructions):
        update_instructions = []
        section = 'USDT-M'
        for asset, amount in instructions[section].items():
            perp_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='perp', asset=asset)
            quart_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='quart', asset=asset)

            pos = self.generate_position.get_close_position_instruction(section=section, market_ticker=quart_ticker,
                                                                        limit_ticker=perp_ticker,
                                                                        total_amount=amount)

            update_instructions.append(pos)

        section = 'COIN-M'
        for asset, amount in instructions[section].items():
            perp_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='perp', asset=asset)

            current_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='current',
                                                                           asset=asset)
            next_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='next', asset=asset)

            amount = int(math.ceil(amount / 2))

            update_instructions.append(
                self.generate_position.get_close_position_instruction(section=section, market_ticker=current_ticker,
                                                                      limit_ticker=perp_ticker,
                                                                      total_amount=amount))

            update_instructions.append(
                self.generate_position.get_close_position_instruction(section=section, market_ticker=next_ticker,
                                                                      limit_ticker=perp_ticker,
                                                                      total_amount=amount))

        return update_instructions
