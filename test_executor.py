from strategy import FundingExecutor

api_key = ''
secret_key = ''

ticker_swap = 'ETHUSDT'
ticker_futures = 'ETHUSDT_211231'

swap_side = 'buy'
futures_side = 'sell'
reduce_only = False
total_amount = 0.02
section = 'USDT-M'

FundingExecutor(api_key=api_key, secret_key=secret_key, section=section)._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section=section)
