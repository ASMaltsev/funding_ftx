hyperparams = {
    'USDT-M':
        {
            'max_leverage': 8.0,
            'assets':
                {
                'BTC':
                    {
                        'max_share_current_quart': 0.4,
                    },
                'ETH':
                    {
                        'max_share_current_quart': 0.6,
                    }
            }
        },

    'COIN-M':
        {
            'BTC':
                {
                    'max_leverage_perp': 3.0,
                    'max_leverage_current_quart': 3.0,
                    'max_leverage_current_next': 3.0,

                    'max_share_current_quart': 0.6,
                    'max_share_next_quart': 0.6,
                },

            'ETH':
                {
                    'max_leverage_perp': 3.0,
                    'max_leverage_current_quart': 3.0,
                    'max_leverage_current_next': 3.0,

                    'max_share_current_quart': 0.6,
                    'max_share_next_quart': 0.6,
                }
        }
}
