import pandas as pd
from strategy.data_provider import BinanceDataProvider


class Analyze:

    def __init__(self, provider: BinanceDataProvider):

        self.provider = provider

    def analyze_account_coin_m(self):
        account_info = self.provider.get_account_info()
        bases = ['ETH'] # <------ здесь base коины для коин м написать
        for base in bases:
            assets = [base]
            total_balance = {}
            for asset_info in account_info['tickers']:
                asset = asset_info['ticker']
                if asset in assets:
                    total_balance[asset] = min(float(asset_info['walletBalance']), float(asset_info['marginBalance']))

            real_leverage_df = pd.DataFrame(index=assets, columns=['perp', 'current', 'next'])
            for asset in assets:
                perp_ticker = base + 'USD_PERP'
                current_ticker = base + 'USD_220325'
                next_ticker = base + 'USD_220624'

                real_leverage_df.loc[asset, 'perp'] = self._leverage_coin_m(perp_ticker, total_balance[asset],
                                                                            strategy_amount=0, only_account=True)
                real_leverage_df.loc[asset, 'current'] = self._leverage_coin_m(current_ticker, total_balance[asset],
                                                                               strategy_amount=0, only_account=True)
                real_leverage_df.loc[asset, 'next'] = self._leverage_coin_m(next_ticker, total_balance[asset],
                                                                            strategy_amount=0, only_account=True)

            real_leverage_df = real_leverage_df.astype(float)

            real_leverage_df['quart'] = real_leverage_df['current'] + real_leverage_df['next']
            real_leverage_df['abs_perp'] = real_leverage_df['perp'].abs()
            real_leverage_df['section'] = real_leverage_df[['quart', 'abs_perp']].max(axis=1)
            print(real_leverage_df)

    def _leverage_coin_m(self, ticker, twb, strategy_amount=0, only_account=False):
        if only_account:
            return self.provider.get_amount_positions(ticker) * self.provider.get_contract_size(
                ticker) / (self.provider.get_price(ticker) * twb)
        return abs(strategy_amount) * self.provider.get_contract_size(ticker) / (
                self.provider.get_price(ticker) * twb)

    def _get_amount_ticker_coin_m(self, leverage, twb, ticker_1, ticker_2, ticker_3):
        price = max(self.provider.get_price(ticker_1), self.provider.get_price(ticker_2),
                    self.provider.get_price(ticker_3))
        return leverage * twb * price / self.provider.get_contract_size(ticker_1)

    def analyze_account_usdt_m(self):
        account_info = self.provider.get_account_info()
        print(account_info)
        total_wallet_balance = min(float(account_info['totalWalletBalance']), float(account_info['totalMarginBalance']))
        assets = ['BTC', 'ETH']

        real_leverage_df = pd.DataFrame(index=['perp', 'quart'], columns=assets)

        for asset in assets:
            perp = asset + 'USDT'
            quart = asset + 'USDT_220325'

            real_leverage_df.loc['perp', asset] = self._leverage_usdt_m(ticker=perp, twb=total_wallet_balance,
                                                                        amount_strategy=0, only_account=True)

            real_leverage_df.loc['quart', asset] = self._leverage_usdt_m(ticker=quart, twb=total_wallet_balance,
                                                                         amount_strategy=0, only_account=True)
        real_leverage_df = real_leverage_df.astype(float)
        print(real_leverage_df)

        type_contract = real_leverage_df.sum(axis=1).abs().nlargest(1).index.values[0]
        print(real_leverage_df.loc[type_contract].sum())

    def _leverage_usdt_m(self, ticker, twb, amount_strategy=0, only_account=False):
        if only_account:
            return self.provider.get_amount_positions(ticker) * self.provider.get_price(
                ticker=ticker) / twb
        return abs(amount_strategy) * self.provider.get_price(ticker=ticker) / twb

    def _get_amount_ticker_usdt_m(self, amount, twb, ticker_1, ticker_2):
        return amount * twb / max(self.provider.get_price(ticker_1),
                                  self.provider.get_price(ticker_2))


connector = BinanceDataProvider(
    api_key='', secret_key='', section='COIN-M') # <------ сюда ключи и секция

Analyze(provider=connector).analyze_account_coin_m() # <-------если секция коин м то анализ коин м, если юсдт м то анализ юсдт м
