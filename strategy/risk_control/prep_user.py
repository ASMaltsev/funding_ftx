from strategy.others import API_KEY, SECRET_KEY
from connectors import ConnectorRouter


class Accaunt_set(object):
    """docstring for ."""

    def __init__(self, arg):
        self.arg = arg


        self.connector_coin = ConnectorRouter(exchange='Binance', section='COIN-M').init_connector(api_key, secret_key)
        self.connector_usdt = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector(api_key, secret_key)



    def change_all_lev(lev, section='USDT-M'):

        client = self.connector_usdt if section == 'USDT-M' else self.connector_coin
        tickers = client.get_tickers()
        tickers = [i['ticker'] for i in tickers]

        if section == 'USDT-M':
            time.sleep(5)
        else:
            time.sleep(10)

        for t in tq(tickers):
            try:
                print(client.change_leverage(t, lev))
            except:
                pass

            if section == 'USDT-M':
                time.sleep(0.5)
            else:
                time.sleep(2)

    def get_balances(section='USDT-M', symbols: list):

        client = self.connector_usdt if section == 'USDT-M' else self.connector_coin
        balances = client.get_balances()

        for b in balances:
            if b.key()
