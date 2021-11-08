import pandas as pd
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.hyperparams import AccountHyperParams, ProviderHyperParamsStrategy
from strategy.logging import Logger

logger = Logger('Rebalancer').create()


class Rebalancer:
    def __init__(self, data_provider_usdt_m: BinanceDataProvider, data_provider_coin_m: BinanceDataProvider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.provider_hyperparams_account = AccountHyperParams()
        self.provider_hyperparams_strategy = ProviderHyperParamsStrategy()
        self.safety_coef = 0.05

    def analyze_account(self) -> dict:
        # coin_m_close = self._analyze_account_coin_m()
        usdt_m_close = self._analyze_account_usdt_m()
        return {'USDT-M': usdt_m_close, 'COIN-M': 0}

    def _analyze_account_usdt_m(self):
        account_info = self.data_provider_usdt_m.get_account_info()
        total_wallet_balance = float(account_info['totalWalletBalance'])
        available_balance = float(account_info['availableBalance'])
        section = 'USDT-M'
        account_max_leverage = self.provider_hyperparams_account.get_max_leverage(section=section)
        assets = self.provider_hyperparams_strategy.get_assets(section)

        if available_balance / total_wallet_balance > self.safety_coef:
            return {asset: 0.0 for asset in assets}
        else:
            leverage_df = pd.DataFrame(index=['perp', 'quart'], columns=assets)
            for asset in assets:
                leverage_df.loc['perp', asset] = self._leverage_usdt_m(
                    ticker=self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                  kind='perp'),
                    twb=total_wallet_balance)

                leverage_df.loc['quart', asset] = self._leverage_usdt_m(
                    ticker=self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                  kind='quart'),
                    twb=total_wallet_balance)
            leverage_df = leverage_df.astype(float)

            type_contract = leverage_df.sum(axis=1).abs().nlargest(1).index.values[0]
            delta = abs(leverage_df.loc[type_contract].sum()) - account_max_leverage

            close_series = leverage_df.loc[type_contract].copy()
            close_series = close_series / close_series.sum() * delta
            result = {}

            for asset, amount in close_series.items():
                ticker_perp = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                     kind='perp')
                ticker_quart = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                      kind='quart')

                result[asset] = self._get_amount_ticker_usdt_m(amount, total_wallet_balance, ticker_perp, ticker_quart)
            return result

    def _leverage_usdt_m(self, ticker, twb):
        return self.data_provider_usdt_m.get_amount_positions(ticker) * self.data_provider_usdt_m.get_price(
            ticker=ticker) / twb

    def _leverage_coin_m(self, ticker):
        return self.data_provider_coin_m.get_amount_positions(ticker) * self.data_provider_coin_m.get_contract_size(
            ticker) / self.data_provider_coin_m.get_price(ticker)

    def _get_amount_ticker_usdt_m(self, amount, twb, ticker_1, ticker_2):
        return amount * twb / max(self.data_provider_usdt_m.get_price(ticker_1),
                                  self.data_provider_usdt_m.get_price(ticker_2))
