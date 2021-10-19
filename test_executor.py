from strategy import FundingExecutor

api_key = ''
secret_key = ''

ticker_swap = 'ETHUSDT'
ticker_futures = 'ETHUSDT_211231'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = True
total_amount = 0.08

FundingExecutor(api_key=api_key, secret_key=secret_key)._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount)
