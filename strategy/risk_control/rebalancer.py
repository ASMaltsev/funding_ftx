import pandas as pd
import math
import copy
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.logging import Logger

logger = Logger('Rebalancer').create()


class Rebalancer:

    def __init__(self, data_provider_usdt_m: BinanceDataProvider, data_provider_coin_m: BinanceDataProvider,
                 hyperparams_provider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.provider_hyperparams = hyperparams_provider
        self.safety_coef = 0.05

    def analyze_account(self, strategy_instructions, real_position_quart, real_position_perp):
        transform_instructions, strategy_amount = self._transform_strategy(strategy_instructions,
                                                                           real_position_quart,
                                                                           real_position_perp)
        res = {}
        if 'USDT-M' in self.provider_hyperparams.get_sections():
            res.update({'USDT-M': self._analyze_account_usdt_m(transform_instructions['USDT-M'],
                                                               strategy_amount['USDT-M'])})
        if 'COIN-M' in self.provider_hyperparams.get_sections():
            res.update({'COIN-M': self._analyze_account_coin_m(transform_instructions['COIN-M'])})
        return res, strategy_amount

    def _transform_strategy(self, strategy_instructions, real_position_quart, real_position_perp):
        transform_instructions = {'USDT-M': {}, 'COIN-M': {}}
        real_position = {}
        real_position.update(real_position_perp)
        real_position.update(real_position_quart)
        sections = set()
        for strategy_instruction in strategy_instructions:
            limit_ticker = strategy_instruction['limit_ticker']
            market_ticker = strategy_instruction['market_ticker']
            amount_limit_ticker = self._get_sign(strategy_instruction['limit_side']) * strategy_instruction[
                'total_amount']
            amount_market_ticker = self._get_sign(strategy_instruction['market_side']) * strategy_instruction[
                'total_amount']

            current_amount_limit_ticker = transform_instructions[strategy_instruction['section']].get(limit_ticker, 0)
            current_amount_market_ticker = transform_instructions[strategy_instruction['section']].get(market_ticker, 0)
            sections.add(strategy_instruction['section'])
            transform_instructions[strategy_instruction['section']].update(
                {limit_ticker: current_amount_limit_ticker + amount_limit_ticker,
                 market_ticker: current_amount_market_ticker + amount_market_ticker})

        strategy_amount = copy.deepcopy(transform_instructions)
        for pair in real_position.keys():
            for section in sections:
                transform_instructions[section][pair] = transform_instructions[section].get(pair, 0) + real_position[
                    pair]

        logger.info(msg='Strategy instruction with real positions in Rebalancer.',
                    extra=dict(transform_instructions=transform_instructions))
        logger.info(msg='Strategy instruction in Rebalancer.',
                    extra=dict(strategy_amount=strategy_amount))
        return transform_instructions, strategy_amount

    @staticmethod
    def _get_sign(side):
        if side == 'sell':
            return -1
        elif side == 'buy':
            return 1

    def _analyze_account_coin_m(self, amount_instructions):
        section = 'COIN-M'
        account_info = self.data_provider_coin_m.get_account_info()
        assets = self.provider_hyperparams.get_assets(section=section)
        account_max_leverage = self.provider_hyperparams.get_max_leverage('COIN-M')
        total_balance = {}
        for asset_info in account_info['tickers']:
            asset = asset_info['ticker']
            if asset in assets:
                total_balance[asset] = min(float(asset_info['walletBalance']), float(asset_info['marginBalance']))
        leverage_df = pd.DataFrame(index=assets, columns=['perp', 'current', 'next'])
        real_leverage_df = pd.DataFrame(index=assets, columns=['perp', 'current', 'next'])
        for asset in assets:
            perp_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                        kind='perp')
            current_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                           kind='current')
            next_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                        kind='next')

            leverage_df.loc[asset, 'perp'] = self._leverage_coin_m(perp_ticker, total_balance[asset],
                                                                   strategy_amount=amount_instructions.get(perp_ticker,
                                                                                                           0))
            leverage_df.loc[asset, 'current'] = self._leverage_coin_m(current_ticker, total_balance[asset],
                                                                      strategy_amount=amount_instructions.get(
                                                                          current_ticker, 0))
            leverage_df.loc[asset, 'next'] = self._leverage_coin_m(next_ticker, total_balance[asset],
                                                                   strategy_amount=amount_instructions.get(next_ticker,
                                                                                                           0))

            real_leverage_df.loc[asset, 'perp'] = self._leverage_coin_m(perp_ticker, total_balance[asset],
                                                                        strategy_amount=0, only_account=True)
            real_leverage_df.loc[asset, 'current'] = self._leverage_coin_m(current_ticker, total_balance[asset],
                                                                           strategy_amount=0, only_account=True)
            real_leverage_df.loc[asset, 'next'] = self._leverage_coin_m(next_ticker, total_balance[asset],
                                                                        strategy_amount=0, only_account=True)

        leverage_df = leverage_df.astype(float)
        real_leverage_df = real_leverage_df.astype(float)

        leverage_df['quart'] = leverage_df['current'] + leverage_df['next']
        leverage_df['abs_perp'] = leverage_df['perp'].abs()
        leverage_df['section'] = leverage_df[['quart', 'abs_perp']].max(axis=1)
        leverage_df = leverage_df[['perp', 'current', 'next', 'section']]
        leverage_df['delta'] = leverage_df['section'] - account_max_leverage

        real_leverage_df['quart'] = real_leverage_df['current'] + real_leverage_df['next']
        real_leverage_df['abs_perp'] = real_leverage_df['perp'].abs()
        real_leverage_df['section'] = real_leverage_df[['quart', 'abs_perp']].max(axis=1)

        logger.info(msg='COIN-M leverages info after strategy:', extra=dict(leverage_df=leverage_df))
        logger.info(msg='COIN-M real leverages info:', extra=dict(leverage_df=real_leverage_df))

        result = {}
        for asset in assets:
            perp_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                        kind='perp')
            current_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                           kind='current')
            next_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                        kind='next')

            if real_leverage_df.loc[asset, 'section'] > self.provider_hyperparams.get_max_leverage(section=section):

                leverage = 0 if leverage_df.loc[asset, 'delta'] < self.provider_hyperparams.get_max_ignore(
                    section=section) else leverage_df.loc[asset, 'delta']
                if leverage == 0:
                    result[asset] = -1 * amount_instructions[asset + 'USD_PERP']
                else:
                    result[asset] = max(0, math.ceil(self._get_amount_ticker_coin_m(leverage=leverage,
                                                                                    twb=total_balance[asset],
                                                                                    ticker_1=perp_ticker,
                                                                                    ticker_2=current_ticker,
                                                                                    ticker_3=next_ticker)))
            else:
                if leverage_df.loc[asset, 'delta'] < 0:
                    result[asset] = 0
                else:
                    result[asset] = max(0, math.ceil(
                        self._get_amount_ticker_coin_m(leverage=abs(leverage_df.loc[asset, 'delta']),
                                                       twb=total_balance[asset],
                                                       ticker_1=perp_ticker,
                                                       ticker_2=current_ticker,
                                                       ticker_3=next_ticker)))

        return result

    def _leverage_coin_m(self, ticker, twb, strategy_amount=0, only_account=False):
        if only_account:
            return self.data_provider_coin_m.get_amount_positions(ticker) * self.data_provider_coin_m.get_contract_size(
                ticker) / (self.data_provider_coin_m.get_price(ticker) * twb)
        return abs(strategy_amount) * self.data_provider_coin_m.get_contract_size(ticker) / (
                self.data_provider_coin_m.get_price(ticker) * twb)

    def _get_amount_ticker_coin_m(self, leverage, twb, ticker_1, ticker_2, ticker_3):
        price = max(self.data_provider_coin_m.get_price(ticker_1), self.data_provider_coin_m.get_price(ticker_2),
                    self.data_provider_coin_m.get_price(ticker_3))
        return leverage * twb * price / self.data_provider_coin_m.get_contract_size(ticker_1)

    def _analyze_account_usdt_m(self, amount_after_strategy, adjusted_instruction):
        account_info = self.data_provider_usdt_m.get_account_info()
        total_wallet_balance = min(float(account_info['totalWalletBalance']), float(account_info['totalMarginBalance']))
        section = 'USDT-M'
        account_max_leverage = self.provider_hyperparams.get_max_leverage(section=section)
        assets = self.provider_hyperparams.get_assets(section)
        leverage_df = pd.DataFrame(index=['perp', 'quart'], columns=assets)
        real_leverage_df = pd.DataFrame(index=['perp', 'quart'], columns=assets)

        for asset in assets:
            perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                 kind='perp')
            quart = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                  kind='quart')
            leverage_df.loc['perp', asset] = self._leverage_usdt_m(ticker=perp, twb=total_wallet_balance,
                                                                   amount_strategy=amount_after_strategy.get(perp, 0))

            leverage_df.loc['quart', asset] = self._leverage_usdt_m(ticker=quart, twb=total_wallet_balance,
                                                                    amount_strategy=amount_after_strategy.get(perp, 0))

            real_leverage_df.loc['perp', asset] = self._leverage_usdt_m(ticker=perp, twb=total_wallet_balance,
                                                                        amount_strategy=0, only_account=True)

            real_leverage_df.loc['quart', asset] = self._leverage_usdt_m(ticker=quart, twb=total_wallet_balance,
                                                                         amount_strategy=0, only_account=True)

        leverage_df = leverage_df.astype(float)
        real_leverage_df = real_leverage_df.astype(float)
        logger.info(msg='USDT-M leverages with strategies info:', extra=dict(leverage_df=leverage_df))
        logger.info(msg='USDT-M real leverages info:', extra=dict(real_leverage_df=real_leverage_df))

        type_contract = leverage_df.sum(axis=1).abs().nlargest(1).index.values[0]
        delta = abs(leverage_df.loc[type_contract].sum()) - account_max_leverage

        type_contract = real_leverage_df.sum(axis=1).abs().nlargest(1).index.values[0]
        real_delta = abs(real_leverage_df.loc[type_contract].sum()) - account_max_leverage
        logger.info(msg='Delta leverages.', extra=dict(delta=delta, real_delta=real_delta))
        if real_delta > 0:
            delta = 0 if delta < self.provider_hyperparams.get_max_ignore(section=section) else delta
            if delta == 0:
                res = dict()
                for asset in assets:
                    res[asset] = -1 * adjusted_instruction.get(asset + 'USDT', 0)
                return res

        if delta <= 0:
            return {asset: 0.0 for asset in assets}
        close_series = leverage_df.loc[type_contract].copy()
        close_series = close_series.abs()
        close_series = close_series / close_series.sum() * delta
        result = {}
        perp_tickers = set()
        for asset, amount in close_series.items():
            ticker_perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                        kind='perp')
            perp_tickers.add(ticker_perp)
            ticker_quart = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                         kind='quart')

            result[asset] = max(0, self._get_amount_ticker_usdt_m(amount, total_wallet_balance, ticker_perp,
                                                                  ticker_quart))

        logger.info(msg='Final result rebalancer', extra=dict(result=result))
        residue, change_strategy = self._rebalance_result(adjusted_instruction, result)
        residue = round(residue, 4)
        res = {}
        if residue <= 0:
            for asset in change_strategy.keys():
                perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='perp')
                res[asset] = abs(adjusted_instruction[perp]) - change_strategy[asset]
        else:
            for asset, amount in close_series.items():
                ticker_perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                            kind='perp')
                perp_tickers.add(ticker_perp)
                ticker_quart = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                             kind='quart')

                res[asset] = max(0, self._get_amount_ticker_usdt_m(
                    residue / self.data_provider_usdt_m.get_price(ticker=asset + 'USDT'), total_wallet_balance,
                    ticker_perp,
                    ticker_quart))
        return res

    def _rebalance_result(self, adjusted_instruction, close_amount):
        section = 'USDT-M'
        total_neg_usdt = 0
        change_strategy_asset = {}
        for asset in close_amount.keys():
            perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='perp')
            total_neg_usdt += abs(
                min((abs(adjusted_instruction.get(perp, 0)) - close_amount[
                    asset]) * self.data_provider_usdt_m.get_price(
                    ticker=asset + 'USDT'), 0))

            change_strategy_asset[asset] = max(abs(adjusted_instruction.get(perp, 0)) - close_amount[asset], 0)
        residue = total_neg_usdt
        if total_neg_usdt > 0:
            for asset in change_strategy_asset.keys():
                if change_strategy_asset[asset] > 0:
                    asset_amount = total_neg_usdt / self.data_provider_usdt_m.get_price(ticker=asset + 'USDT')
                    residue -= round(
                        change_strategy_asset[asset] * self.data_provider_usdt_m.get_price(ticker=asset + 'USDT'), 4)
                    change_strategy_asset[asset] = max((change_strategy_asset[asset] - asset_amount, 0))
        return residue, change_strategy_asset

    def _leverage_usdt_m(self, ticker, twb, amount_strategy=0, only_account=False):
        if only_account:
            return self.data_provider_usdt_m.get_amount_positions(ticker) * self.data_provider_usdt_m.get_price(
                ticker=ticker) / twb
        return abs(amount_strategy) * self.data_provider_usdt_m.get_price(ticker=ticker) / twb

    def _get_amount_ticker_usdt_m(self, amount, twb, ticker_1, ticker_2):
        return amount * twb / max(self.data_provider_usdt_m.get_price(ticker_1),
                                  self.data_provider_usdt_m.get_price(ticker_2))
