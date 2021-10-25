from strategy.executor import FundingExecutor
from constants import *

FundingExecutor(api_key=api_key, secret_key=secret_key, section=section)._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section=section)
