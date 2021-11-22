from connectors import ConnectorRouter
import time

class Accaunt_set():

    def __init__(self, api_key, secret_key):

        self.api_key = api_key
        self.secret_key = secret_key
        self.connector_coin = ConnectorRouter(exchange='Binance', section='COIN-M').init_connector(api_key, secret_key)
        self.connector_usdt = ConnectorRouter(exchange='Binance', section='USDT-M').init_connector(api_key, secret_key)



    def change_all_lev(self, lev, section):
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


    def get_balances(self, section, symbols: list):
        client = self.connector_usdt if section == 'USDT-M' else self.connector_coin
        balances = client.get_balances().items()

        for symbol, value in balances:
            if symbol in symbols:
                b = value['total']
                print(f'{symbol}: {b}')


    def get_positions(self, section):
        client = self.connector_usdt if section == 'USDT-M' else self.connector_usdt
        positions = client.get_positions()

        for p in positions:
            if p['positionAmt'] != 0:
                ticker = p['ticker']
                amount = p['positionAmt']
                print(f'{ticker}: {amount}')
