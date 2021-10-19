import json
import random
import asyncio
import websockets
from threading import Thread
from strategy.others import Logger

logger = Logger('WebSocket').create()


class BinanceOrderBook(Thread):

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
        self.state = None

    def run(self) -> None:
        stream_url = f'{self.base_url}/ws/{self.ticker}@bookTicker'
        self.loop.run_until_complete(self._connect_ws(stream_url))
        logger.info(msg='Websocket connected')
        self.loop.run_until_complete(self._subscribe())
        logger.info(msg='Websocket subscribed')
        self.loop.run_until_complete(self._receive_messages())

    def get_state(self):
        return self.state

    async def _connect_ws(self, url):
        self.ws = await websockets.connect(url, ping_interval=360)

    async def _subscribe(self):
        self.id = random.randint(1, 9999)
        payload = {"method": "SUBSCRIBE",
                   "params": [f'{self.ticker}@bookTicker'],
                   "id": self.id}
        await self.ws.send(json.dumps(payload))

    async def _receive_messages(self):
        while True:
            message = await self.ws.recv()
            await self._process_message(json.loads(message))

    async def _process_message(self, message):
        if message.get('e') == 'bookTicker' and message.get('s') == self.ticker.upper():
            if self.state is None or int(message.get('u')) > int(self.state.get('u')):
                self.state = message
        else:
            logger.warning(msg=f'Incorrect message = {message}')
