from strategy.executor.binance_executor.executor import BinanceExecutor

from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from params import *

kwargs = {
    'market_ticker': ticker_futures, 'limit_ticker': ticker_swap,
    'limit_side': swap_side, 'market_side': futures_side,
    'total_amount': total_amount, 'reduce_only': reduce_only
}

data_provider = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section=section)
BinanceExecutor(data_provider).execute(**kwargs)
