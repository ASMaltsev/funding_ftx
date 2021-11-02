strategy_hyperparams = {
    'base_fr_earn': 0.1095,
    # 0.04
    'A': -0.4,
    'k': 0.0495,
    'time_exit': 9,
    'save_time': lambda x: x + 5,
    'USDT-M':
        {
            'share':
                {
                    'BTC': 0.4,
                    'ETH': 0.6
                },
            'assets':
                {
                    'ETH':
                        {
                            'perp': 'ETHUSDT',
                            'quart': 'ETHUSDT_211231',
                        },
                    'BTC':
                        {
                            'perp': 'BTCUSDT',
                            'quart': 'BTCUSDT_211231',
                        },
                }
        },
    'COIN-M':
        {
            'share':
                {
                    'current': 0.5,
                    'next': 0.5
                },
            'assets':
                {
                    'ETH':
                        {
                            'perp': 'ETHUSD_PERP',
                            'current': 'ETHUSD_211231',
                            'next': 'ETHUSD_220325',
                        },
                    'BTC':

                        {
                            'perp': 'ETHUSD_PERP',
                            'current': 'ETHUSD_211231',
                            'next': 'ETHUSD_220325',
                        }
                }
        }
}

account_hyperparams = {
    'USDT-M':
        {
            'leverage_max': 3.0,
        },
    'COIN-M':
        {
            'leverage_max': 3.0,
        }
}
