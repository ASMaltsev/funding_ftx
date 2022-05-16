#!/usr/bin/env python

from strategy.executor.ftx_executor.executor import FtxExecutor

api_key = ''
secret_key = ''

FtxExecutor(api_key=api_key, secret_key=secret_key, section='', market_ticker='BTC-0624',
            limit_ticker='BTC-PERP', limit_side='SELL', market_side='BUY', total_amount=0.001,
            reduce_only=False, limit_amount=0.0001).execute()
