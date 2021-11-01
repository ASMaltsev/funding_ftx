from strategy.hyperparams.hyperparameters import hyperparams
from enum import Enum


class TypeActive(Enum):
    CURRENT_QUART = 'current_quart'
    NEXT_QUART = 'next_quart'
    PERP = 'perp'


class ProviderHyperParams:

    @staticmethod
    def get_max_share(section: str, asset: str, type_active: TypeActive):
        return hyperparams[section][asset]['max_share_' + type_active.value]

    @staticmethod
    def get_max_leverage(section: str):
        return 8.0

    @staticmethod
    def get_all_assets(section: str):
        return ['BTC', 'ETH']

    @staticmethod
    def get_futures(section, asset):
        if section == 'COIN-M':
            if asset == 'ETH':
                return ('ETHUSD_PERP', 'ETHUSD_211231', 'ETHUSD_220325')
            elif asset == 'BTC':
                return ('BTCUSD_PERP', 'BTCUSD_211231', 'BTCUSD_220325')
