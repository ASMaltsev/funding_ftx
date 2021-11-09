from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.logging import Logger
from strategy.risk_control import RealStatePositions, Rebalancer
from strategy.translation import TranslateStrategyInstructions, TranslateLeverage
from strategy.alpha import FundingAlpha
from strategy.hyperparams import ProviderHyperParamsStrategy
from strategy.executor.binance_executor.executor import BinanceExecutor

logger = Logger('DadExecutor').create()


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        self.data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
        self.data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')
        self.hyperparams_provider = ProviderHyperParamsStrategy()

    def execute(self):
        while True:
            executor_instructions = self._generate_instructions()
            for executor_instruction in executor_instructions:
                batches = self._generate_batches(executor_instruction)
                for batch in batches:
                    BinanceExecutor(self.api_key, self.secret_key, **batch).execute()
                    break
                break

    def _generate_instructions(self):
        instructions = FundingAlpha().decide()

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
                try:
                    del pre_final_instruction['strategy_section']
                except KeyError:
                    pass
                final_instructions.append(pre_final_instruction.copy())

        logger.info(msg='Final instructions:', extra=dict(final_instructions=final_instructions))
        return final_instructions

    @staticmethod
    def _correction_strategy_position(strategy_positions, real_quart_positions):
        update_strategy_positions = []

        for strategy_position in strategy_positions:
            real_amount = real_quart_positions.get(strategy_position['market_ticker'], 0) \
                          + real_quart_positions.get(strategy_position['limit_ticker'], 0)
            if strategy_position['strategy_section'] == 'setup':
                strategy_position['total_amount'] = max(0, strategy_position['total_amount'] - real_amount)
            elif strategy_position['strategy_section'] == 'exit':
                strategy_position['total_amount'] = min(strategy_position['total_amount'], real_amount)
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
                        if strategy_instruction['strategy_section'] == 'exit':
                            rebalancer_instruction['total_amount'] = max(strategy_instruction['total_amount'],
                                                                         rebalancer_instruction['total_amount'])
                        update_instructions.append(rebalancer_instruction.copy())
        return update_instructions

    def _generate_batches(self, instruction: dict) -> list:
        assets = self.hyperparams_provider.get_assets(instruction['section'])
        min_batch_size = 0
        for asset in assets:
            if instruction['limit_ticker'].startswith(asset):
                min_batch_size = self.hyperparams_provider.get_min_batch_size(instruction['section'], asset)
        count = int(instruction['total_amount'] / min_batch_size)
        if count == 0:
            return [instruction]
        instruction['total_amount'] /= count
        return count * [instruction]
