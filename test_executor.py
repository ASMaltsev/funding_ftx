from strategy import FundingExecutor

api_key = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
secret_key = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'

ticker_swap = 'ETHUSD_PERP'
ticker_futures = 'ETHUSD_211231'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = False
total_amount = 6

FundingExecutor(api_key=api_key, secret_key=secret_key, section='COIN-M')._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section='COIN-M')
