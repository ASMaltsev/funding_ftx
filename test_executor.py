from strategy import FundingExecutor

#ShSh1
api_key = 'cgi94unJMvafiMFPwcvy115hDxSIqVjecPtpUTFEno92ldJlG57x2vBVPzsWzbG9'
secret_key = 'C6PiycF8lSHUuULY4BnvbpPPZinxs9vaFmlHGLazStYbW5qSTM96OsahQNR6dnR0'

ticker_swap = 'BTCUSD_PERP'
ticker_futures = 'BTCUSD_220325'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = False
total_amount = 10

FundingExecutor(api_key=api_key, secret_key=secret_key, section='COIN-M')._execute(
    market_ticker=ticker_futures,
    market_side=futures_side,
    limit_ticker=ticker_swap,
    limit_side=swap_side,
    reduce_only=reduce_only,
    total_amount=total_amount,
    section='COIN-M')
