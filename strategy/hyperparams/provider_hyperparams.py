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
    def get_max_leverage(section: str, type_active: TypeActive):
        return 8.0

    @staticmethod
    def get_all_assets(section: str):
        return ['BTC', 'ETH']
