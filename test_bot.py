from strategy.risk_control import TelegramBot

final_instructions = \
    [
        {'market_ticker': 'ETHUSD_211231', 'limit_ticker': 'ETHUSD_PERP', 'total_amount': 10.5, 'section': 'COIN-M',
         'limit_side': 'sell', 'market_side': 'buy', 'reduce_only': True},
        {'market_ticker': 'ETHUSD_220325', 'limit_ticker': 'ETHUSD_PERP', 'total_amount': 10.5, 'section': 'COIN-M',
         'limit_side': 'sell', 'market_side': 'buy', 'reduce_only': True},
        {'market_ticker': 'BTCUSD_220325', 'limit_ticker': 'BTCUSD_PERP', 'total_amount': 2.0, 'section': 'COIN-M',
         'limit_side': 'sell', 'market_side': 'buy', 'reduce_only': False}]

real_positions = {'ETHUSDT_211231': 0.05, 'BTCUSDT_211231': 0.002, 'ETHUSD_211231': 30.0, 'BTCUSD_211231': 0.0,
                  'ETHUSD_220325': 30.0, 'BTCUSD_220325': 4.0, 'ETHUSDT': -0.05, 'BTCUSDT': -0.002,
                  'ETHUSD_PERP': -60.0,
                  'BTCUSD_PERP': -4.0}

tb = TelegramBot()
tb.start(final_instructions, real_positions)
