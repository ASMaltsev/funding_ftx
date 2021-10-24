from strategy.executor.tools.funding_tools.executor import FundingExecutor

# # TEST API
api_key = ''
secret_key = ''

ticker_swap = 'ETHUSD_PERP'
ticker_futures = 'ETHUSD_211231'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = False
total_amount = 100
section = 'COIN-M'

FundingExecutor(api_key=api_key, secret_key=secret_key, section=section)._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section=section)
