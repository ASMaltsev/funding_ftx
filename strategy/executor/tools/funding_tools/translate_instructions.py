from strategy.hyperparameters import hyperparams
from strategy.executor.tools.funding_tools.binance_data_provider import BinanceDataProvider


class TranslateInstructions:

    def __init__(self, data_provider_usdt_m: BinanceDataProvider, data_provider_coin_m: BinanceDataProvider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m

    def parse(self, instructions: dict):
        instructions_usdt_m = instructions.get('USDT-M')
        executor_usdt_m, executor_coin_m = [], []
        if instructions_usdt_m is not None:
            executor_usdt_m = self._parse(instructions_usdt_m['actions'], 'USDT-M')

        instructions_coin_m = instructions.get('COIN-M')
        if instructions_coin_m is not None:
            executor_coin_m = self._parse(instructions_coin_m['actions'], 'COIN-M')
        return executor_usdt_m, executor_coin_m

    def _parse(self, instructions_section: dict, section: str):
        executor_instructions = []
        for coin in instructions_section.keys():
            coin_actions = instructions_section[coin]
            work = coin_actions[0]
            part = coin_actions[1]
            pairs = coin_actions[2]
            if work == 'exit':
                self._parse_exit(part=part, pairs=pairs, section=section, ticker='')
            elif work == 'setup':
                executor_instructions.append(
                    self._parse_setup(part=part, perp_ticker=pairs[0], quart_ticker=pairs[1], section=section,
                                      coin=coin))
        return executor_instructions

    def _parse_setup(self, part: float, perp_ticker: str, quart_ticker: str, section: str, coin: str):
        if section == 'USDT-M':
            total_amount = self._size_usdt_m(part, quart_ticker)
        elif section == 'COIN-M':
            ticker = coin.split('_')[0]
            total_amount = self._size_coin_m(part, quart_ticker, ticker)
        else:
            raise NotImplementedError

        return {'market_ticker': quart_ticker, 'limit_ticker': perp_ticker, 'limit_side': 'sell',
                'market_side': 'buy', 'total_amount': total_amount, 'reduce_only': False, 'section': section}

    def _parse_exit(self, part: float, pairs: tuple, section: str, ticker: str):
        pass

    def _size_usdt_m(self, part: float, quart_ticker: str) -> float:
        leverage = hyperparams['USDT-M']['leverage_quart']
        total_balance = self.data_provider_usdt_m.get_account_info()['totalWalletBalance']
        precision = len(str(self.data_provider_usdt_m.min_size_for_market_order(quart_ticker)).split('.'))
        price = self.data_provider_usdt_m.get_price(quart_ticker)
        return float(f"{total_balance * leverage * part / price:.{precision}f}")

    def _size_coin_m(self, part: float, perp_ticker: str, ticker: str) -> float:
        leverage = hyperparams['COIN-M']['leverage_quart_current']
        total_balance = 0
        account_info = self.data_provider_coin_m.get_account_info()
        for info_ticker in account_info['tickers']:
            if info_ticker['ticker'] == 'ETH':
                total_balance = info_ticker['walletBalance']
        price_perp = self.data_provider_coin_m.get_price(ticker=perp_ticker)
        contract_price = 0
        for symbols_info in self.data_provider_coin_m.get_exchange_info()['symbols']:
            if symbols_info['symbol'] == perp_ticker:
                contract_price = float(symbols_info['contractSize'])
        return float(str(total_balance * leverage * part * price_perp / contract_price).split('.')[0])
