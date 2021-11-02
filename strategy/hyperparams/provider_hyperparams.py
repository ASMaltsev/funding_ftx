from strategy.hyperparams.hyperparameters import hyperparams
from enum import Enum


class TypeActive(Enum):
    CURRENT_QUART = 'current_quart'
    NEXT_QUART = 'next_quart'
    PERP = 'perp'


class ProviderHyperParams:
