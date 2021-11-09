from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.others import inverse_operation
from strategy.logging import Logger
from strategy.risk_control import RealStatePositions, Rebalancer
from strategy.translation import TranslateStrategyInstructions, TranslateLeverage

logger = Logger('DadExecutor').create()


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        self.data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
        self.data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')

    def execute(self, instructions: dict):
        strategy_instructions = TranslateStrategyInstructions(self.data_provider_usdt_m,
                                                              self.data_provider_coin_m).parse(instructions)

        logger.info(msg='Strategy instructions:', extra=dict(strategy_instructions=strategy_instructions))

        real_position_quart, real_position_perp = RealStatePositions(data_provider_usdt_m=self.data_provider_usdt_m,
                                                                     data_provider_coin_m=self.data_provider_coin_m) \
            .get_positions()

        logger.info(msg='Real positions:',
                    extra=dict(real_position_quart=real_position_quart, real_position_perp=real_position_perp))

        update_instructions = self._correction_strategy_position(strategy_instructions, real_position_quart)

        logger.info(msg='Adjusted positions:', extra=dict(instructions=update_instructions))

        rebalancer_instructions = Rebalancer(data_provider_usdt_m=self.data_provider_usdt_m,
                                             data_provider_coin_m=self.data_provider_coin_m).analyze_account()

        logger.info(msg='Rebalancer instructions:', extra=dict(rebalancer_instructions=rebalancer_instructions))

        close_positions = TranslateLeverage(
            data_provider_usdt_m=self.data_provider_usdt_m,
            data_provider_coin_m=self.data_provider_coin_m).translate(rebalancer_instructions)

        logger.info(msg='Close positions:', extra=dict(close_positions=close_positions))

        pre_final_instructions = self._union_instructions(update_instructions, close_positions)
        logger.info(msg='Pre final instructions:', extra=dict(pre_final_instructions=pre_final_instructions))

        final_instructions = []
        for pre_final_instruction in pre_final_instructions:
            if pre_final_instruction['total_amount'] > 0:
                final_instructions.append(pre_final_instruction.copy())

        logger.info(msg='Final instructions:', extra=dict(final_instructions=final_instructions))
        return final_instructions

    @staticmethod
    def _correction_strategy_position(strategy_positions, real_quart_positions):
        update_strategy_positions = []

        for strategy_position in strategy_positions:
            real_amount = real_quart_positions.get(strategy_position['market_ticker'],
                                                   0) + real_quart_positions.get(
                strategy_position['limit_ticker'], 0)
            strategy_position['total_amount'] -= real_amount  # TODO: если стратегия setup то amount=0, а если выход
            if strategy_position['total_amount'] < 0:
                strategy_position['total_amount'] = abs(strategy_position['total_amount'])
                strategy_position['limit_side'] = inverse_operation(strategy_position['limit_side'])
                strategy_position['market_side'] = inverse_operation(strategy_position['market_side'])

            update_strategy_positions.append(strategy_position.copy())
        return update_strategy_positions

    @staticmethod
    def _union_instructions(strategy_instructions, rebalancer_instructions):
        update_instructions = []
        for strategy_instruction in strategy_instructions:
            for rebalancer_instruction in rebalancer_instructions:
                if strategy_instruction['market_ticker'] == rebalancer_instruction['market_ticker'] and \
                        strategy_instruction['limit_ticker'] == rebalancer_instruction['limit_ticker']:
                    if rebalancer_instruction['total_amount'] == 0:
                        update_instructions.append(strategy_instruction.copy())
                    else:
                        update_instructions.append(rebalancer_instruction.copy())
        return update_instructions
