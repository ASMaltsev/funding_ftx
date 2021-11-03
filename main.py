from strategy.alpha import FundingAlpha
from strategy.executor import DadExecutor
from strategy.executor.binance_executor.executor import BinanceExecutor

api_key = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
secret_key = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'

instructions = FundingAlpha().decide()
DadExecutor(api_key=api_key, secret_key=secret_key).execute(instructions)

"""
ticker_swap = 'ETHUSDT'
ticker_futures = 'ETHUSDT_211231'

swap_side = 'sell'
futures_side = 'buy'
reduce_only = False
total_amount = 0.01
section = 'USDT-M'

BinanceExecutor(api_key=api_key, secret_key=secret_key, section=section, market_ticker=ticker_futures,
                limit_ticker=ticker_swap, limit_side=swap_side, market_side=futures_side, total_amount=total_amount,
                reduce_only=reduce_only).execute()
"""
