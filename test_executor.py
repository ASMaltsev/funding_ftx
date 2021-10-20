from strategy import FundingExecutor

#YM
api_key  = 'QRjSmxIXbjCujcDH4FFn9YobT9B0e52diGa68JbuAGCHUCoOqaq3Ppig4KhhX3i2'
secret_key = 't4EFPmyOdhqxdMz27QUcikK4srXRrvmPgL4rlXWvFtrMR6bEjCAnXQIrhu8CFY79'

ticker_swap = 'BTCUSD_PERP'
ticker_futures = 'BTCUSD_211231'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = False
total_amount = 4677

FundingExecutor(api_key=api_key, secret_key=secret_key, section='COIN-M')._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section='COIN-M')
