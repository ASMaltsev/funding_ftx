from fast_execution import FastStrategy
from tools.funding_tools.data_provider_funding import DataProviderFunding

from connectors import ConnectorRouter

# import sys
# sys.path.insert(1, '../../Connectors_v0.1/')
# from router import ConnectorRouter


# # TEST API
api_key = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
secret_key = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'


if __name__ == "__main__":

    ticker_swap = 'ETHUSDT'
    ticker_futures = 'ETHUSDT_211231'

    swap_side = 'sell'
    futures_side = 'buy'

    reduce_only = False
    limit_amount = 0.01
    total_amount = 0.03

    client = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector(api_key, secret_key)
    data_provider = DataProviderFunding(client)

    start = FastStrategy(client=client,
                         data_provider = data_provider,
                         market_ticker=ticker_futures,
                         market_ticker_side=futures_side,

                         limit_ticker=ticker_swap,
                         limit_ticker_side=swap_side,
                         limit_amount=limit_amount,

                         reduce_only=reduce_only,
                         total_amount=total_amount)
    start.set_position()
