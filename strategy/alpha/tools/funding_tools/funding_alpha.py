from strategy.alpha.tools.abstract_tools import AbstractAlpha
from strategy.logging import Logger
from strategy.data_provider import BinanceDataProvider

import itertools

logger = Logger('Alpha').create()


class FundingAlpha(AbstractAlpha):

    def __init__(self, provider_hyperparams):
        self.sections = provider_hyperparams.get_sections()
        self.base_fr_earn = provider_hyperparams.get_base_fr_earn()
        self.A = provider_hyperparams.get_A()
        self.k = provider_hyperparams.get_k()
        self.time_exit = provider_hyperparams.get_time_exit()
        self.save_time = provider_hyperparams.get_save_time()
        self.share_usdt_m = []
        self.list_usdt_m = []

        self.share_coin_m = []
        self.list_coin_m = []
        self.state = {}

        logger.info(msg='Create strategy for with params:',
                    extra=dict(base_fr_earn=self.base_fr_earn, A=self.A, k=self.k, time_exit=self.time_exit,
                               save_time=self.save_time))

        if 'USDT-M' in self.sections:
            self.share_usdt_m = provider_hyperparams.get_share(section='USDT-M')
            self.list_usdt_m = provider_hyperparams.get_all_tickers(section='USDT-M')
            self.data_provider_usdt_m = BinanceDataProvider(api_key='', secret_key='', section='USDT-M')

            logger.info(msg='Params for USDT-M:',
                        extra=dict(share_usdt_m=self.share_usdt_m, list_usdt_m=self.list_usdt_m))
            self.state.update({'USDT-M': {'actions': {}}})

        if 'COIN-M' in self.sections:
            self.share_coin_m = provider_hyperparams.get_share(section='COIN-M')
            self.list_coin_m = provider_hyperparams.get_all_tickers(section='COIN-M')
            self.data_provider_coin_m = BinanceDataProvider(api_key='', secret_key='', section='COIN-M')
            self.state.update({'COIN-M': {'actions': {}}})

        logger.info(msg='Params for USDT-M:',
                    extra=dict(share_usdt_m=self.share_usdt_m, list_usdt_m=self.list_usdt_m))

    def decide(self) -> dict:
        pairs_usdt_m, pairs_coin_m = self.list_parser()

        share_coin_m = self.share_coin_m.copy()

        if 'COIN-M' in self.sections:
            share_coin_m['next'] = [max(self.get_current_next(pairs_coin_m)), share_coin_m['next']]
            share_coin_m['current'] = [min(self.get_current_next(pairs_coin_m)), share_coin_m['current']]

        state = self.state.copy()
        state = self.setup(state, pairs_usdt_m, pairs_coin_m, share_coin_m)
        state = self.exit_position(state, self.time_exit)
        return state

    # Setup
    def setup(self, state, pairs_usdt_m, pairs_coin_m, share_coin_m):
        if 'USDT-M' in self.sections:
            for pair_usdt_m in pairs_usdt_m:
                asset = 'BTC' if pair_usdt_m[0].startswith('BTC') else 'ETH'
                size, spread_pct, spread_apr = self.get_clam_size(self.k, pair_usdt_m[0], pair_usdt_m[1],
                                                                  self.data_provider_usdt_m)

                logger.info(msg='Spread:', extra=dict(tickers=pair_usdt_m, spread=spread_apr))
                if spread_apr < 0:
                    size = 1
                else:
                    size = min(1, size)
                    if self.base_fr_earn - spread_apr > self.A:
                        tte = self.data_provider_usdt_m.get_tte(pair_usdt_m[1])
                        if tte <= self.save_time:
                            size = size
                        else:
                            size = 1

                if 0 <= size <= 1:
                    state['USDT-M']['actions'][asset] = ['setup', size * self.share_usdt_m[asset], pair_usdt_m]

        elif 'COIN-M' in self.sections:
            for pair_coin_m in pairs_coin_m:
                asset = 'BTC' if pair_coin_m[0].startswith('BTC') else 'ETH'
                quart = 'current' if int(pair_coin_m[1].split('_')[1]) == share_coin_m['current'][0] else 'next'
                size, spread_pct, spread_apr = self.get_clam_size(self.k, pair_coin_m[0], pair_coin_m[1],
                                                                  self.data_provider_coin_m)

                logger.info(msg='Spread:', extra=dict(tickers=pair_coin_m, spread=spread_apr))
                if spread_apr < 0:
                    size = 1
                else:
                    size = min(1, size)

                    if self.base_fr_earn - spread_apr > self.A:
                        tte = self.data_provider_coin_m.get_tte(pair_coin_m[1])
                        if tte <= self.save_time:
                            size = size
                        else:
                            size = 1

                if 0 <= size <= 1:
                    state['COIN-M']['actions'][f'{asset}_{quart}'] = ['setup', size * share_coin_m[quart][1],
                                                                      pair_coin_m]

        return state

    def exit_position(self, state, time_exit):
        for s in self.sections:
            assets = list(state[s]['actions'].keys())
            data_provider = self.data_provider_usdt_m if s == 'USDT-M' else self.data_provider_coin_m
            for asset in assets:
                pair = state[s]['actions'][asset][-1]
                q = state[s]['actions'][asset][-1][-1]
                tte = data_provider.get_tte(q)
                if tte <= time_exit:
                    state[s]['actions'][asset] = ['exit', 1, pair]
        return state

    @staticmethod
    def get_clam_size(k, ticker_swap, ticker_quart, data_provider):
        spread_pct, spread_apr = data_provider.get_spread(ticker_swap, ticker_quart)
        return (k / spread_apr), spread_pct, spread_apr

    def list_parser(self):
        pairs_usdt_m = []
        pairs_coin_m = []
        for pair in itertools.product(self.list_usdt_m, repeat=2):
            name = pair[0].split('_')
            if name[0][-1] == 'T':
                if len(name) == 1:
                    if len(pair[1].split('_')) > 1:
                        if pair[1].split('_')[0] == name[0]:
                            pairs_usdt_m.append(pair)

        for pair in itertools.product(self.list_coin_m, repeat=2):
            name = pair[0].split('_')
            if name[1] == 'PERP':
                if pair[1].split('_')[1] != 'PERP':
                    if name[0] == pair[1].split('_')[0]:
                        pairs_coin_m.append(pair)
        return pairs_usdt_m, pairs_coin_m

    @staticmethod
    def get_current_next(pairs_coin_m):
        quarts = list(set([int(q[1].split('_')[1]) for q in pairs_coin_m]))
        return quarts
