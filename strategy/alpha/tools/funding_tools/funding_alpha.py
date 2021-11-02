from strategy.alpha.tools.abstract_tools import AbstractAlpha
from strategy.alpha.tools.funding_tools.alpha_data_provider_binance import DataProviderFunding
from strategy.others import Logger

import time
import itertools


class FundingAlpha(AbstractAlpha):

    def __init__(self, list_usdtm, list_coinm, A, k, time_exit, save_time, share_usdtm, share_coinm, base_fr_earn):

        self.base_fr_earn = base_fr_earn
        self.A = A
        self.k = k
        self.time_exit = time_exit
        self.save_time = save_time

        self.share_usdtm = share_usdtm
        self.share_coinm = share_coinm

        self.list_coinm = list_coinm  # ['ETHUSDT', 'BTCUSDT', 'ETHUSDT_211231', 'BTCUSDT_211231']
        self.list_usdtm = list_usdtm  # ['ETHUSD_PERP', 'BTCUSD_PERP', 'BTCUSD_211231', 'ETHUSD_211231', 'BTCUSD_220325', 'ETHUSD_220325']

        self.dataprovider = DataProviderFunding()

        self.state = {
            'USDT-M': {'actions': {}},
            'COIN-M': {'actions': {}}
        }

        self.logger = Logger('strategy').create()

    def decide(self) -> dict:
        pairs_usdtm, pairs_coinm = self.list_parser()

        share_coinm = self.share_coinm.copy()
        share_coinm['next'] = [max(self.get_current_next(pairs_coinm)), share_coinm['next']]
        share_coinm['current'] = [min(self.get_current_next(pairs_coinm)), share_coinm['current']]

        state = self.setup(self.state, pairs_usdtm, pairs_coinm, self.time_exit, share_coinm)
        state = self.exit_position(self.state, self.time_exit)

        return state

    # Setup
    def setup(self, state, pairs_usdtm, pairs_coinm, time_exit, share_coinm):

        for pair_usdtm in pairs_usdtm:
            asset = 'BTC' if pair_usdtm[0].startswith('BTC') else 'ETH'
            size, spread_pct, spread_apr = self.get_clam_size(self.k, pair_usdtm[0], pair_usdtm[1])

            if spread_apr < 0:
                size = 1

            else:
                size = min(1, size)
                if self.base_fr_earn - spread_apr > self.A:
                    tte = self.dataprovider.get_tte(pair_usdtm[1])
                    if tte <= self.save_time:
                        size = size
                    else:
                        size = 1

            if 0 <= size <= 1:
                state['USDT-M']['actions'][asset] = ['setup', size * self.share_usdtm[asset], pair_usdtm]

        for pair_coinm in pairs_coinm:
            asset = 'BTC' if pair_coinm[0].startswith('BTC') else 'ETH'
            quart = 'current' if int(pair_coinm[1].split('_')[1]) == share_coinm['current'][0] else 'next'
            size, spread_pct, spread_apr = self.get_clam_size(self.k, pair_coinm[0], pair_coinm[1])
            size = min(1, size)

            if self.base_fr_earn - spread_apr > self.A:
                tte = self.dataprovider.get_tte(pair_coinm[1])
                if tte <= self.save_time:
                    size = size
                else:
                    size = 1

            if 0 <= size <= 1:
                state['COIN-M']['actions'][f'{asset}_{quart}'] = ['setup', size * share_coinm[quart][1], pair_coinm]

        return state

    def exit_position(self, state, time_exit):
        sections = ['USDT-M', 'COIN-M']
        for s in sections:
            assets = list(state[s]['actions'].keys())
            for asset in assets:
                pair = state[s]['actions'][asset][-1]
                q = state[s]['actions'][asset][-1][-1]
                tte = self.dataprovider.get_tte(q)
                if tte <= time_exit:
                    state[s]['actions'][asset] = ['exit', 0, pair]

        return state

    def get_clam_size(self, k, ticker_swap, ticker_quart):  # k = 4.95
        spread_pct, spread_apr = self.dataprovider.get_spread(ticker_swap, ticker_quart)
        return (k / spread_apr), spread_pct, spread_apr

    def list_parser(self):
        pairs_usdtm = []
        pairs_coinm = []
        for pair in itertools.product(self.list_usdtm, repeat=2):
            name = pair[0].split('_')
            if name[0][-1] == 'T':
                if len(name) == 1:
                    if len(pair[1].split('_')) > 1:
                        if pair[1].split('_')[0] == name[0]:
                            pairs_usdtm.append(pair)

        for pair in itertools.product(self.list_coinm, repeat=2):
            name = pair[0].split('_')
            if name[1] == 'PERP':
                if pair[1].split('_')[1] != 'PERP':
                    if name[0] == pair[1].split('_')[0]:
                        pairs_coinm.append(pair)

        return pairs_usdtm, pairs_coinm

    def get_current_next(self, pairs_coinm):
        quarts = list(set([int(q[1].split('_')[1]) for q in pairs_coinm]))
        return quarts
