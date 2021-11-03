from joblib import Parallel, delayed
from strategy.executor.binance_executor.executor import BinanceExecutor

api_key = ''
secret_key = ''

kwargs_ETH_USDT_M = {
    'api_key': api_key,
    'secret_key': secret_key,

    'limit_ticker': 'ETHUSDT',
    'market_ticker': 'ETHUSDT_211231',

    'market_side': 'sell',
    'limit_side': 'buy',

    'reduce_only': False,
    'total_amount': 0.01,
    'section': 'USDT-M',
}

kwargs_BTC_USDT_M = {
    'api_key': api_key,
    'secret_key': secret_key,

    'limit_ticker': 'BTCUSDT',
    'market_ticker': 'BTCUSDT_211231',

    'market_side': 'sell',
    'limit_side': 'buy',

    'reduce_only': False,
    'total_amount': 0.01,
    'section': 'USDT-M',
}

kwargs_ETH_COIN_M = {
    'api_key': api_key,
    'secret_key': secret_key,

    'limit_ticker': 'ETHUSD_PERP',
    'market_ticker': 'ETHUSD_211231',

    'market_side': 'sell',
    'limit_side': 'buy',

    'reduce_only': False,
    'total_amount': 1,
    'section': 'COIN-M',
}

kwargs_BTC_COIN_M = {
    'api_key': api_key,
    'secret_key': secret_key,

    'limit_ticker': 'BTCUSD_PERP',
    'market_ticker': 'BTCUSD_211231',

    'market_side': 'sell',
    'limit_side': 'buy',

    'reduce_only': False,
    'total_amount': 1,
    'section': 'COIN-M',
}

kwargs_arr = [kwargs_ETH_USDT_M, kwargs_BTC_USDT_M, kwargs_ETH_COIN_M, kwargs_BTC_COIN_M]


def execute(**kwargs):
    executor = BinanceExecutor(**kwargs)
    executor.execute()


Parallel(n_jobs=4)(delayed(execute)(**kwargs) for kwargs in kwargs_arr)
