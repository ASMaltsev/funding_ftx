import json
import random
import asyncio
import websockets
from threading import Thread, Lock
from strategy.logging import Logger

logger = Logger('WebSocket').create()


class WebSocketStream(Thread):
    RECONNECT_INTERVAL = 23 * 60 * 60

    def __init__(self, ticker: str, section: str):
        super().__init__()
        if section == 'USDT-M':
            self.base_url = 'wss://fstream.binance.com'
        elif section == 'COIN-M':
            self.base_url = 'wss://dstream.binance.com'
        else:
            raise KeyError('Wrong section')
        self.ticker = ticker.lower()
        self.stream_url = f'{self.base_url}/ws/{self.ticker}@bookTicker'
        self.loop = asyncio.get_event_loop()
        self.connect_lock = Lock()
        self.ws = None
        self.id = None
        self.state = None

    def run(self) -> None:
        self.loop.run_until_complete(self._connect_ws(self.stream_url))
        logger.info('Connected')
        self.loop.run_until_complete(self._subscribe())
        logger.info('Subscribed')
        self.loop.run_until_complete(asyncio.gather(self._receive_messages(), self._daily_reconnect(), loop=self.loop))

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

    async def _daily_reconnect(self):
        while True:
            await asyncio.sleep(self.RECONNECT_INTERVAL)
            with self.connect_lock:
                logger.info('Start reconnecting...')
                await self._connect_ws(self.stream_url)
                await self._subscribe()
                logger.info('Reconnected')

    async def _receive_messages(self):
        while True:
            message = await self.ws.recv()
            await self._process_message(json.loads(message))

    async def _process_message(self, message):
        if message.get('e') == 'bookTicker' and message.get('s') == self.ticker.upper():
            if self.state is None or message.get('u') > self.state.get('u'):
                self.state = message
        else:
            logger.warning(msg=message)
