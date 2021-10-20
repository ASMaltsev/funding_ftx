from strategy import FundingExecutor

api_key = ''
secret_key = ''

ticker_swap = 'ETHUSD_PERP'
ticker_futures = 'ETHUSD_211231'

swap_side = 'buy'
futures_side = 'sell'
reduce_only = False
total_amount = 3

FundingExecutor(api_key=api_key, secret_key=secret_key, section='COIN-M')._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section='COIN-M')
