strategy_hyperparams = {
    'base_fr_earn': 0.1095,
    'A': 0.04,
    'k': 0.0495,
    'time_exit': 9,
    'save_time': lambda x: x + 5,
    'USDT-M':
        {
            'share':
                {
                    'BTC': 0.375,
                    'ETH': 0.575
                },
            'assets':
                {
                    'ETH':
                        {
                            'perp': 'ETHUSDT',
                            'quart': 'ETHUSDT_211231',
                            'min_batch_size': 0.1,
                        },
                    'BTC':
                        {
                            'perp': 'BTCUSDT',
                            'quart': 'BTCUSDT_211231',
                            'min_batch_size': 0.03,
                        },
                }
        },
    # 'COIN-M':
    #     {
    #         'share':
    #             {
    #                 'current': 0.475,
    #                 'next': 0.475
    #             },
    #         'assets':
    #             {
    #                 'ETH':
    #                     {
    #                         'perp': 'ETHUSD_PERP',
    #                         'current': 'ETHUSD_211231',
    #                         'next': 'ETHUSD_220325',
    #                         'min_batch_size': 10,
    #                     },
    #                 'BTC':
    #
    #                     {
    #                         'perp': 'BTCUSD_PERP',
    #                         'current': 'BTCUSD_211231',
    #                         'next': 'BTCUSD_220325',
    #                         'min_batch_size': 5,
    #                     }
    #             }
    #     }
}

account_hyperparams = {
    'USDT-M':
        {
            'leverage_max': 10,
            'max_ignore': 0.2,
        },
    'COIN-M':
        {
            'leverage_max': 10,
            'max_ignore': 0.2,
        }
}
