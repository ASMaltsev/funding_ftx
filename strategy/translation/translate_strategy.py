from strategy.hyperparams import AccountHyperParams
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.logging import Logger
from strategy.translation.position_info import GeneratePosition

my_logger = Logger('TranslateInstructions')
logger = my_logger.create()


class TranslateStrategyInstructions:

    def __init__(self, data_provider_usdt_m: BinanceDataProvider, data_provider_coin_m: BinanceDataProvider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.account_hyperparams = AccountHyperParams()
        self.generate_position = GeneratePosition()

    def parse(self, instructions: dict):

        instructions_usdt_m = instructions.get('USDT-M')
        executor_usdt_m, executor_coin_m = [], []
        if instructions_usdt_m is not None:
            executor_usdt_m = self._parse(instructions_usdt_m['actions'], 'USDT-M')

        instructions_coin_m = instructions.get('COIN-M')
        if instructions_coin_m is not None:
            executor_coin_m = self._parse(instructions_coin_m['actions'], 'COIN-M')

        return executor_usdt_m + executor_coin_m

    def _parse(self, instructions_section: dict, section: str):

        executor_instructions = []
        for coin in instructions_section.keys():
            coin_actions = instructions_section[coin]
            work = coin_actions[0]
            part = coin_actions[1]
            perp_ticker, quart_ticker = coin_actions[2]
            if work == 'exit':
                res = self._parse_exit(part=part, quart_ticker=quart_ticker, section=section,
                                       perp_ticker=perp_ticker)
                res['strategy_section'] = 'exit'
                executor_instructions.append(res)
            elif work == 'setup':
                res = self._parse_setup(part=part, perp_ticker=perp_ticker,
                                        quart_ticker=quart_ticker, section=section,
                                        coin=coin)
                res['strategy_section'] = 'setup'
                executor_instructions.append(res)
            return executor_instructions

    def _parse_setup(self, part: float, perp_ticker: str, quart_ticker: str, section: str, coin: str) -> dict:
        if section == 'USDT-M':
            total_amount = self._size_usdt_m(part, quart_ticker)
        elif section == 'COIN-M':
            ticker = coin.split('_')[0]
            total_amount = self._size_coin_m(part, ticker, perp_ticker)
        else:
            raise NotImplementedError
        return self.generate_position.get_open_position_instruction(section=section, market_ticker=quart_ticker,
                                                                    limit_ticker=perp_ticker,
                                                                    total_amount=total_amount)

    def _parse_exit(self, part: float, quart_ticker: str, section: str, perp_ticker: str) -> dict:
        # Exit shows what proportion of assets needs to be closed
        # Ex: If Exit = 1. It's mean that we have to close all
        total_amount = self._size_exit(part, quart_ticker, section)
        return self.generate_position.get_close_position_instruction(section=section, market_ticker=quart_ticker,
                                                                     limit_ticker=perp_ticker,
                                                                     total_amount=total_amount)

    def _size_exit(self, part: float, quart_ticker: str, section: str) -> float:
        if section == 'USDT-M':
            amt = self.data_provider_usdt_m.get_amount_positions(quart_ticker)
            result = float(amt * part)
        elif section == 'COIN-M':
            amt = self.data_provider_coin_m.get_amount_positions(quart_ticker)
            result = int(amt * part)
        else:
            raise NotImplementedError

        return result

    def _size_usdt_m(self, part: float, quart_ticker: str) -> float:
        leverage = self.account_hyperparams.get_max_leverage(section='USDT-M')
        total_balance = self.data_provider_usdt_m.get_account_info()['totalWalletBalance']
        precision = self._precision(quart_ticker)
        price = self.data_provider_usdt_m.get_price(quart_ticker)
        result = float(f"{total_balance * leverage * part / price:.{precision}f}")
        logger.info(msg='Calculation size for USDT-M',
                    extra=dict(quart_ticker=quart_ticker, total_balance=total_balance, leverage=leverage,
                               price=price, part=part, result=result))
        return result

    @staticmethod
    def _precision(ticker: str):
        if ticker.startswith('ETH'):
            return 2
        elif ticker.startswith('BTC'):
            return 3

    def _size_coin_m(self, part: float, asset: str, perp_ticker: str) -> float:
        leverage = self.account_hyperparams.get_max_leverage(section='COIN-M')
        total_balance = 0
        account_info = self.data_provider_coin_m.get_account_info()
        for info_ticker in account_info['tickers']:
            if info_ticker['ticker'] == asset:
                total_balance = info_ticker['walletBalance']

        price_perp = self.data_provider_coin_m.get_price(ticker=perp_ticker)
        contract_price = 0
        for symbols_info in self.data_provider_coin_m.get_exchange_info()['symbols']:
            if symbols_info['symbol'] == perp_ticker:
                contract_price = float(symbols_info['contractSize'])
        result = float(str(total_balance * leverage * part * price_perp / contract_price).split('.')[0])
        logger.info(msg='Calculation size for COIN-M',
                    extra=dict(perp_ticker=perp_ticker, total_balance=total_balance, leverage=leverage,
                               price_perp=price_perp, contract_price=contract_price, part=part, result=result))
        return result
