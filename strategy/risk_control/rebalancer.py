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
        return {'USDT-M': self._analyze_account_usdt_m(), 'COIN-M': self._analyze_account_coin_m()}

    def _analyze_account_coin_m(self):
        section = 'COIN-M'
        account_info = self.data_provider_coin_m.get_account_info()
        assets = self.provider_hyperparams_strategy.get_assets(section=section)
        account_max_leverage = self.provider_hyperparams_account.get_max_leverage('COIN-M')
        total_balance = {}
        for asset_info in account_info['tickers']:
            asset = asset_info['ticker']
            if asset in assets:
                total_balance[asset] = asset_info['walletBalance']
        leverage_df = pd.DataFrame(index=assets, columns=['perp', 'current', 'next'])
        for asset in assets:
            perp_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                 kind='perp')
            current_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                    kind='current')
            next_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                 kind='next')
            leverage_df.loc[asset, 'perp'] = self._leverage_coin_m(perp_ticker)
            leverage_df.loc[asset, 'current'] = self._leverage_coin_m(current_ticker)
            leverage_df.loc[asset, 'next'] = self._leverage_coin_m(next_ticker)
        leverage_df = leverage_df.astype(float)

        leverage_df['quart'] = leverage_df['current'] + leverage_df['next']
        leverage_df['abs_perp'] = leverage_df['perp'].abs()
        leverage_df['section'] = leverage_df[['quart', 'abs_perp']].max(axis=1)
        leverage_df = leverage_df[['perp', 'current', 'next', 'section']]
        leverage_df['delta'] = leverage_df['section'] - account_max_leverage
        result = {}
        for asset in assets:
            perp_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                 kind='perp')
            current_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                    kind='current')
            next_ticker = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                 kind='next')

            result[asset] = max(0, round(self._get_amount_ticker_coin_m(leverage=leverage_df.loc[asset, 'delta'],
                                                                        twb=total_balance[asset], ticker_1=perp_ticker,
                                                                        ticker_2=current_ticker, ticker_3=next_ticker),
                                         0))
        return result

    def _leverage_coin_m(self, ticker):
        return self.data_provider_coin_m.get_amount_positions(ticker) * self.data_provider_coin_m.get_contract_size(
            ticker) / self.data_provider_coin_m.get_price(ticker)

    def _get_amount_ticker_coin_m(self, leverage, twb, ticker_1, ticker_2, ticker_3):
        price = max(self.data_provider_coin_m.get_price(ticker_1), self.data_provider_coin_m.get_price(ticker_2),
                    self.data_provider_coin_m.get_price(ticker_3))
        return leverage * twb * price / self.data_provider_coin_m.get_contract_size(ticker_1)

    def _analyze_account_usdt_m(self):
        account_info = self.data_provider_usdt_m.get_account_info()
        total_wallet_balance = float(account_info['totalWalletBalance'])
        section = 'USDT-M'

        account_max_leverage = self.provider_hyperparams_account.get_max_leverage(section=section)
        assets = self.provider_hyperparams_strategy.get_assets(section)
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
        if delta < 0:
            return {asset: 0.0 for asset in assets}

        close_series = leverage_df.loc[type_contract].copy()
        close_series = close_series.abs()
        close_series = close_series / close_series.sum() * delta
        result = {}
        for asset, amount in close_series.items():
            ticker_perp = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                 kind='perp')
            ticker_quart = self.provider_hyperparams_strategy.get_ticker_by_asset(section=section, asset=asset,
                                                                                  kind='quart')

            result[asset] = max(0, self._get_amount_ticker_usdt_m(amount, total_wallet_balance, ticker_perp,
                                                                  ticker_quart))
        return result

    def _leverage_usdt_m(self, ticker, twb):
        return self.data_provider_usdt_m.get_amount_positions(ticker) * self.data_provider_usdt_m.get_price(
            ticker=ticker) / twb

    def _get_amount_ticker_usdt_m(self, amount, twb, ticker_1, ticker_2):
        return amount * twb / max(self.data_provider_usdt_m.get_price(ticker_1),
                                  self.data_provider_usdt_m.get_price(ticker_2))
