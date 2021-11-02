hyperparams = {
    'base_fr_earn': 0.1095,
    'A': 0.04,
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
                }
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

base_fr_earn = 0.1095
A = 0.04
k = 0.0495
time_exit = 9
save_time = time_exit + 5
share_usdt_m = {'BTC': 0.4,
                'ETH': 0.6}

share_coinm = {'current': 0.5,
               'next': 0.5}

list_usdtm = ['ETHUSDT', 'BTCUSDT', 'ETHUSDT_211231', 'BTCUSDT_211231']
list_coinm = ['ETHUSD_PERP', 'BTCUSD_PERP', 'BTCUSD_211231', 'ETHUSD_211231', 'BTCUSD_220325', 'ETHUSD_220325']
