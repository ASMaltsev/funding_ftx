import sys
import time
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.logging import Logger
from strategy.risk_control import RealStatePositions, Rebalancer
from strategy.translation import TranslateStrategyInstructions, TranslateLeverage
from strategy.alpha import FundingAlpha
from strategy.hyperparams import HyperParams
from strategy.risk_control import TelegramBot
from strategy.risk_control import AccountPosition
from strategy.executor.binance_executor.executor import BinanceExecutor
from strategy.translation import GeneratePosition

logger = Logger('DadExecutor').create()


class DadExecutor:

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        self.data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
        self.data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')

    def execute(self):
        hyperparams_provider = HyperParams()
        hyperparams_provider.update_data()

        account_info = AccountPosition(self.data_provider_usdt_m, self.data_provider_coin_m, hyperparams_provider)

        send_message = True
        flag = False

        while True:

            hyperparams_provider.update_data()
            account_info.control()

            executor_instructions = self._generate_instructions(send_message=send_message,
                                                                hyperparams_provider=hyperparams_provider)
            send_message = False
            if len(executor_instructions) == 0:
                if not flag:
                    bot = TelegramBot()
                    positions = RealStatePositions(data_provider_coin_m=self.data_provider_coin_m,
                                                   data_provider_usdt_m=self.data_provider_usdt_m,
                                                   hyperparams_provider=hyperparams_provider).get_positions()
                    bot.send_message(msg='FINISH')
                    bot.send_message(msg=str(positions))
                time.sleep(120)
                send_message = True
                flag = True
            else:
                flag = False
                logger.info(msg='Executor instructions: ', extra=dict(executor_instructions=executor_instructions))
                batches = self._generate_batches(executor_instructions, hyperparams_provider)
                logger.info(msg='Batches: ', extra=dict(batches=batches))
                for batch in batches:
                    BinanceExecutor(self.api_key, self.secret_key, **batch).execute()

    def _generate_instructions(self, send_message, hyperparams_provider):
        phrase = 'skip'
        final_instructions = []
        while phrase == 'skip':
            hyperparams_provider.update_data()
            instructions = FundingAlpha(hyperparams_provider).decide()
            logger.info(msg='Strategy instructions:', extra=dict(instructions=instructions))

            strategy_instructions = TranslateStrategyInstructions(self.data_provider_usdt_m,
                                                                  self.data_provider_coin_m,
                                                                  hyperparams_provider).parse(instructions)

            logger.info(msg='Translate strategy instructions:', extra=dict(strategy_instructions=strategy_instructions))

            real_position_quart, real_position_perp = RealStatePositions(data_provider_usdt_m=self.data_provider_usdt_m,
                                                                         data_provider_coin_m=self.data_provider_coin_m,
                                                                         hyperparams_provider=hyperparams_provider) \
                .get_positions()

            logger.info(msg='Real positions:',
                        extra=dict(real_position_quart=real_position_quart, real_position_perp=real_position_perp))

            correction_instructions = self._correction_strategy_position(strategy_instructions, real_position_quart)

            logger.info(msg='Adjusted positions:', extra=dict(instructions=correction_instructions))

            rebalancer_instructions, strategy_positions = Rebalancer(data_provider_usdt_m=self.data_provider_usdt_m,
                                                                     data_provider_coin_m=self.data_provider_coin_m,
                                                                     hyperparams_provider=hyperparams_provider) \
                .analyze_account(correction_instructions, real_position_quart, real_position_perp)

            logger.info(msg='Rebalancer instructions:', extra=dict(rebalancer_instructions=rebalancer_instructions))

            close_positions = TranslateLeverage(
                data_provider_usdt_m=self.data_provider_usdt_m,
                data_provider_coin_m=self.data_provider_coin_m,
                hyperparams_provider=hyperparams_provider).translate(rebalancer_instructions,
                                                                     strategy_positions=strategy_positions)

            logger.info(msg='Close positions', extra=dict(close_positions=close_positions))

            union_instructions = self._union_instructions(correction_instructions, close_positions)

            logger.info(msg='Union instructions', extra=dict(union_instructions=union_instructions))

            tmp_instructions = []
            for pre_final_instruction in union_instructions:
                if pre_final_instruction['total_amount'] > 0:
                    pre_final_instruction['total_amount'] = round(pre_final_instruction['total_amount'],
                                                                  BinanceExecutor.get_precision(
                                                                      pre_final_instruction['limit_ticker']))
                    try:
                        del pre_final_instruction['strategy_section']
                    except KeyError:
                        pass
                tmp_instructions.append(pre_final_instruction.copy())
            final_instructions = []
            for final_instruction in tmp_instructions:
                if final_instruction['total_amount'] > 0:
                    final_instructions.append(final_instruction.copy())

            logger.info(msg='Final instructions:', extra=dict(final_instructions=final_instructions))

            if send_message and len(final_instructions) > 0:
                phrase = self.control_strategy(final_instructions=final_instructions,
                                               real_positions={**real_position_perp, **real_position_quart})
                if phrase == 'skip':
                    time.sleep(5 * 60)
            else:
                phrase = ''
        return final_instructions

    @staticmethod
    def control_strategy(final_instructions, real_positions):
        if len(final_instructions) > 0:
            bot = TelegramBot()
            continue_work = bot.start(final_instructions=final_instructions,
                                      real_positions=real_positions)
            if continue_work == 1:
                bot.send_message('OK')
                return 'ok'
            elif continue_work == 0:
                bot.send_message('STOP')
                sys.exit(0)
            elif continue_work == 2:
                bot.send_message('SKIP')
                return 'skip'

    @staticmethod
    def _correction_strategy_position(strategy_positions, real_quart_positions):
        update_strategy_positions = []
        for strategy_position in strategy_positions:
            strategy_position = strategy_position.copy()
            real_amount = real_quart_positions.get(strategy_position['market_ticker'], 0) \
                          + real_quart_positions.get(strategy_position['limit_ticker'], 0)
            if strategy_position['strategy_section'] == 'setup':
                strategy_position['total_amount'] = max(0, strategy_position['total_amount'] - real_amount)
            elif strategy_position['strategy_section'] == 'exit':
                strategy_position['total_amount'] = min(strategy_position['total_amount'], real_amount)
            update_strategy_positions.append(strategy_position)
        return update_strategy_positions

    @staticmethod
    def _union_instructions(strategy_instructions, rebalancer_instructions):
        update_instructions = []
        for strategy_instruction in strategy_instructions:
            for rebalancer_instruction in rebalancer_instructions:
                if strategy_instruction['market_ticker'] == rebalancer_instruction['market_ticker'] and \
                        strategy_instruction['limit_ticker'] == rebalancer_instruction['limit_ticker']:
                    if strategy_instruction['strategy_section'] == 'exit':
                        rebalancer_instruction['total_amount'] = max(strategy_instruction['total_amount'],
                                                                     rebalancer_instruction['total_amount'])
                        update_instructions.append(rebalancer_instruction.copy())
                    elif strategy_instruction['strategy_section'] == 'setup':
                        amount = strategy_instruction['total_amount'] - rebalancer_instruction['total_amount']
                        if amount >= 0:
                            strategy_instruction['total_amount'] = amount
                            update_instructions.append(strategy_instruction.copy())
                        else:
                            instructions = GeneratePosition().get_close_position_instruction(
                                section=strategy_instruction['section'],
                                market_ticker=strategy_instruction['market_ticker'],
                                limit_ticker=strategy_instruction['limit_ticker'], total_amount=abs(amount))
                            update_instructions.append(instructions.copy())
        return update_instructions

    def _generate_batches(self, instructions, hyperparams_provider) -> list:
        for instruction in instructions:
            assets = hyperparams_provider.get_assets(instruction['section'])
            min_batch_size = 0
            limit_amount = 0
            for asset in assets:
                if instruction['limit_ticker'].startswith(asset):
                    min_batch_size = hyperparams_provider.get_min_batch_size(instruction['section'], asset)
                    limit_amount = hyperparams_provider.get_limit_amount(section=instruction['section'], asset=asset)
                    break
            instruction['total_amount'] = min(min_batch_size, instruction['total_amount'])
            instruction['limit_amount'] = limit_amount
        return instructions
