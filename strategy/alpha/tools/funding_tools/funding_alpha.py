from strategy.alpha.tools.abstract_tools import AbstractAlpha
from strategy.alpha.tools.funding_tools.alpha_data_provider_binance import DataProviderFunding
from strategy.others import Logger

import time
import itertools


# A = 6
# k = 4.95


class FundingAlpha(AbstractAlpha):

    def __init__(self, list_usdtm, list_coinm, A, k, share_usdt, share_coin, base_fr_earn):

        self.base_fr_earn = base_fr_earn
        self.A = A
        self.k = k
        self.base_fr_earn = base_fr_earn

        self.share_usdt = share_usdt
        self.share_coinm = share_coinm



        self.list_coinm = list_coinm # ['ETHUSDT', 'BTCUSDT', 'ETHUSDT_211231', 'BTCUSDT_211231']
        self.list_usdtm = list_usdtm # ['ETHUSD_PERP', 'BTCUSD_PERP', 'BTCUSD_211231', 'ETHUSD_211231', 'BTCUSD_220325', 'ETHUSD_220325']

        self.dataprovider = DataProviderFunding()

        self.logger = Logger('strategy').create()


    def decide(self) -> dict:

        state = {
                 'USDT': {'actions': {}},
                 'COIN-M': {'actions': {}}
                 }

        pairs_usdtm, pairs_coinm = list_parser()
        self.share_coinm['next'] = [max(self.get_current_next(pairs_coinm)), share_coin['next']]
        self.share_coinm['current'] = [min(self.get_current_next(pairs_coinm)), share_coin['current']]



        for pair_usdtm in pairs_usdtm:
            pair_usdtm


        return {}


    def get_clam_size(self, k, ticker_swap, ticker_quart): # k = 4.95
        spread_pct, spread_apr = dataprovider.get_spread(ticker_swap, ticker_quart)
        return (k/spread_apr)


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
