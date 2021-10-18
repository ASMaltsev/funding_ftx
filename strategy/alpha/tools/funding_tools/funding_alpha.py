from strategy.alpha.tools.abstract_tools import AbstractAlpha
from strategy.alpha.tools.funding_tools.alpha_data_provider_binance import DataProviderFunding
from strategy.others import Logger


class FundingAlpha(AbstractAlpha):

    def __init__(self):
        self.provider_coin_m = DataProviderFunding(section='COIN-M')
        self.provider_usdt_m = DataProviderFunding(section='USDT-M')
        self.logger = Logger('strategy').create()

    def decide(self) -> dict:
        bbid, bask = self.provider_usdt_m.get_bbid_bask('ETHUSDT')
        self.logger.info(msg='Get data', extra=dict(bbid=bbid, bask=bask))
        return {}
