import json
import random
import asyncio
import websockets
from threading import Thread
from strategy.others import Logger

logger = Logger('WebSocket').create()


class WebSocketStream(Thread):

    def __init__(self, ticker: str, section: str):
        super().__init__()
        if section == 'USDT-M':
            self.base_url = 'wss://fstream.binance.com'
        elif section == 'COIN-M':
            self.base_url = 'wss://dstream.binance.com'
        else:
            raise KeyError('Wrong section')
        self.ticker = ticker.lower()
        self.loop = asyncio.get_event_loop()
        self.ws = None
        self.id = None
        self.state_bbid_ask = None
        # self.state_trades = None

    def run(self) -> None:
        stream_url_book_ticker = f'{self.base_url}/ws/{self.ticker}@bookTicker'
        # stream_url_trades = f'{self.base_url}/ws/{self.ticker}@trade'

        self.loop.run_until_complete(self._connect_ws(stream_url_book_ticker))
        # self.loop.run_until_complete(self._connect_ws(stream_url_trades))
        logger.info(msg='Websockets connected')

        self.loop.run_until_complete(self._subscribe('bookTicker'))
        # self.loop.run_until_complete(self._subscribe('trade'))

        logger.info(msg='Websockets subscribed')
        self.loop.run_until_complete(self._receive_messages())

    def get_state_bbid_ask(self):
        return self.state_bbid_ask

    """
    def get_state_trades(self):
        return self.state_trades
    """

    async def _connect_ws(self, url):
        self.ws = await websockets.connect(url, ping_interval=360)

    async def _subscribe(self, endpoint):
        self.id = random.randint(1, 9999)
        payload = {"method": "SUBSCRIBE",
                   "params": [f'{self.ticker}@{endpoint}'],
                   "id": self.id}
        await self.ws.send(json.dumps(payload))

    async def _receive_messages(self):
        while True:
            message = await self.ws.recv()
            await self._process_message(json.loads(message))

    async def _process_message(self, message):
        if message.get('e') == 'bookTicker' and message.get('s') == self.ticker.upper():
            if self.state_bbid_ask is None or int(message.get('u')) > int(self.state_bbid_ask.get('u')):
                self.state_bbid_ask = message
        # elif message.get('e') == 'trade' and message.get('s') == self.ticker.upper():
        #    if self.state_trades is None or int(message.get('E')) > int(self.state_trades.get('E')):
        #        self.state_trades = message
        else:
            logger.warning(msg=f'Incorrect message = {message}')
