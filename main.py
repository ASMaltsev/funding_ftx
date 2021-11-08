from strategy.alpha import FundingAlpha
from strategy.executor import DadExecutor
from strategy.data_provider.binanace_provider.binance_data_provider import BinanceDataProvider
from strategy.risk_control.rebalancer import Rebalancer

api_key = ''
secret_key = ''

data_provider_usdt_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='USDT-M')
data_provider_coin_m = BinanceDataProvider(api_key=api_key, secret_key=secret_key, section='COIN-M')

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
