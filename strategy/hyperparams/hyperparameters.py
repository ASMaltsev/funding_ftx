strategy_hyperparams = {
    'base_fr_earn': 0.1095,
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
                            'min_batch_size': 2,
                        },
                    'BTC':
                        {
                            'perp': 'BTCUSDT',
                            'quart': 'BTCUSDT_211231',
                            'min_batch_size': 1,
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
                            'min_batch_size': 10,
                        },
                    'BTC':

                        {
                            'perp': 'BTCUSD_PERP',
                            'current': 'BTCUSD_211231',
                            'next': 'BTCUSD_220325',
                            'min_batch_size': 5,
                        }
                }
        }
}

account_hyperparams = {
    'USDT-M':
        {
            'leverage_max': 3,
        },
    'COIN-M':
        {
            'leverage_max': 3,
        }
}
