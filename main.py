from strategy.executor import DadExecutor

if __name__ == '__main__':
    api_key_client = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
    secret_key_client = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'

    executor = DadExecutor(api_key=api_key_client, secret_key=secret_key_client)

    decide = {'USDT-M': {'actions': {'ETH': ['setup',
                                             0.13950666434879383,
                                             ('ETHUSDT', 'ETHUSDT_211231')],
                                     'BTC': ['setup', 0.09514830361427905, ('BTCUSDT', 'BTCUSDT_211231')]}},

              'COIN-M': {'actions': {'ETH_current': ['setup', 0.12, ('ETHUSD_PERP', 'ETHUSD_211231')],
                                     'ETH_next': ['setup', 0.13, ('ETHUSD_PERP', 'ETHUSD_220325')],

                                     'BTC_current': ['exit', 0, ('BTCUSD_PERP', 'BTCUSD_211231')],
                                     'BTC_next': ['exit', 0, ('BTCUSD_PERP', 'BTCUSD_220325')]}}
              }

    executor.execute(instructions=decide, smoke=False)
