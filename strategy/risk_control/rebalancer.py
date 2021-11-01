from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.hyperparams import ProviderHyperParams, TypeActive
from strategy.logging import Logger

logger = Logger('Rebalancer').create()


class Rebalancer:
    def __init__(self, data_provider_usdt_m: BinanceDataProvider, data_provider_coin_m: BinanceDataProvider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.provider_hyperparams = ProviderHyperParams()

    def analyze_account(self) -> dict:
        coin_m_close = self._analyze_account_coin_m()
        usdt_m_close = self._analyze_account_usdt_m()
        return {'USDT-M': usdt_m_close, 'COIN-M': coin_m_close}

    def _analyze_account_usdt_m(self):
        account_info = self.data_provider_usdt_m.get_account_info()
        positions = account_info['positions']
        total_wallet_balance = float(account_info['totalWalletBalance'])
        available_balance = float(account_info['availableBalance'])
        section = 'USDT-M'
        assets = self.provider_hyperparams.get_all_assets(section)
        if available_balance / total_wallet_balance > 1:
            return {asset: 0 for asset in assets}
        else:
            leverages_dict = {}

            for asset in assets:
                for position in positions:
                    if position['symbol'].startswith(asset + 'USDT_'):
                        ticker_quart = position['symbol']
                        current_amount = position['positionAmt']
                        perp = asset + 'USDT'

                        current_price_perp = self.data_provider_usdt_m.get_price(asset + 'USDT')
                        current_price_quart = self.data_provider_usdt_m.get_price(ticker_quart)

                        quart_lev = self._leverage_usdt_m(current_amount=current_amount,
                                                          current_price=current_price_quart,
                                                          twb=total_wallet_balance)

                        perp_lev = self._leverage_usdt_m(current_amount=current_amount,
                                                         current_price=current_price_perp,
                                                         twb=total_wallet_balance)
                        leverages_dict[asset] = {'perp': [perp, perp_lev], 'quart': [ticker_quart, quart_lev]}

            max_leverage = self.provider_hyperparams.get_max_leverage(section=section)
            l_quart = 0
            l_perp = 0
            for asset in leverages_dict.keys():
                l_quart += leverages_dict[asset]['quart'][1]
                l_perp += leverages_dict[asset]['perp'][1]

            current_leverage = max(l_quart, abs(l_perp))

            mean_delta = (current_leverage - max_leverage) / len(leverages_dict.keys())
            if mean_delta <= 0:
                return {asset: 0 for asset in assets}

            rebalance = {}
            for asset, leverages_asset in leverages_dict.items():
                l_asset_quart = float(leverages_asset['quart'][1]) - mean_delta
                l_asset_perp = float(leverages_asset['perp'][1]) - mean_delta
                max_asset_leverage = max(l_asset_perp, l_asset_quart)

                rebalance[asset] = max(0,
                                       max_asset_leverage) * total_wallet_balance / self.data_provider_usdt_m.get_price(
                    ticker=leverages_asset['perp'][0])
            return rebalance

    def _analyze_account_coin_m(self):
        account_info = self.data_provider_coin_m.get_account_info()
        tickers_info = account_info['tickers']
        strategy_tickers = self.provider_hyperparams.get_all_assets('COIN-M')
        balances_dict = {}

        for ticker_info in tickers_info:
            for ticker in strategy_tickers:
                if ticker_info['ticker'] == ticker:
                    balances_dict[ticker] = [ticker_info['availableBalance'], ticker_info['walletBalance']]
        rebalance = {}
        for asset, balances in balances_dict.items():
            try:
                if balances[0] / balances[1] < 0.05:
                    rebalance[asset] = {'volume': 0.0, 'quart': None}
                else:
                    perp, curr_q, next_q = self.provider_hyperparams.get_futures(section='COIN-M', asset=asset)

                    l_perp = self._leverage_coin_m(perp)
                    l_curr = self._leverage_coin_m(curr_q)
                    l_next = self._leverage_coin_m(next_q)
                    l_max = self.provider_hyperparams.get_max_leverage(section='COIN-M')
                    l_account = max(l_curr + l_next, abs(l_perp))
                    delta = max(0, l_account - l_max)

                    volume = delta * balances_dict[asset][1] * self.data_provider_coin_m.get_price(
                        perp) / self.data_provider_coin_m.get_contract_size(perp)

                    rebalance[asset] = {'volume': volume, 'quart': curr_q if l_curr > l_next else next_q}

            except ZeroDivisionError:
                rebalance[asset] = {'volume': 0.0, 'quart': None}
        return rebalance

    @staticmethod
    def _leverage_usdt_m(current_amount, current_price, twb):
        return current_amount * current_price / twb

    def _leverage_coin_m(self, ticker):
        return self.data_provider_coin_m.get_amount_positions(ticker) * self.data_provider_coin_m.get_contract_size(
            ticker) / self.data_provider_coin_m.get_price(ticker)
