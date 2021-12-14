import json
import random
from threading import Thread
from websocket import WebSocketApp


class BinanceWsDataProvider(Thread):

    def __init__(self, ticker: str, section: str):
        super().__init__(daemon=True)
        if section == 'USDT-M':
            self.base_url = 'wss://fstream.binance.com'
        elif section == 'COIN-M':
            self.base_url = 'wss://dstream.binance.com'
        else:
            raise KeyError('Wrong section')
        self.ticker = ticker.lower()
        self.stream_url = f'{self.base_url}/ws/{self.ticker}@bookTicker'
        self._ws = None
        self.id = None
        self.state = None
        self.stopped = False

    def get_state(self) -> dict:
        return self.state.copy()

    def set_ticker(self, ticker: str) -> None:
        self._unsubscribe()
        self.ticker = ticker.lower()
        self.stream_url = f'{self.base_url}/ws/{self.ticker}@bookTicker'
        self._ws.close()

    def stop(self) -> None:
        self.stopped = True
        self._ws.close()

    def run(self) -> None:
        while not self.stopped:
            try:
                self._ws = WebSocketApp(self.stream_url,
                                        on_open=self._wrap_callback(self._on_open),
                                        on_message=self._wrap_callback(self._on_message),
                                        on_close=self._wrap_callback(self._on_close),
                                        on_error=self._wrap_callback(self._on_error))
                self._ws.run_forever(ping_interval=300, ping_timeout=150)
                # self._ws.run_forever()
            except Exception as e:
                print(f'Error in main loop: {e}')
            finally:
                self._ws.close()

    def _wrap_callback(self, f):
        def wrapped_f(ws, *args, **kwargs):
            if ws is self._ws:
                try:
                    f(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')

        return wrapped_f

    def _on_open(self, ws) -> None:
        print('on open')
        self._subscribe()

    def _on_close(self, ws, *args) -> None:
        print('on close')
        self._ws.close()

    def _on_error(self, ws, *args) -> None:
        print('on error')
        print(args)
        self._ws.close()

    def _on_message(self, ws, raw_message: str) -> None:
        message = json.loads(raw_message)
        if message.get('s') == self.ticker.upper():
            self.state = message
        else:
            print(message)

    def _subscribe(self) -> None:
        self.id = random.randint(1, 9999)
        print(f'new id: {self.id}')
        subscription = {"method": "SUBSCRIBE",
                        "params": [f'{self.ticker}@bookTicker'],
                        "id": self.id}
        self._send_json(subscription)
        print(subscription)

    def _unsubscribe(self) -> None:
        unsubscription = {"method": "UNSUBSCRIBE",
                          "params": [f'{self.ticker}@bookTicker'],
                          "id": self.id}
        self._send_json(unsubscription)
        print(unsubscription)

    def _send(self, message) -> None:
        self._ws.send(message)

    def _send_json(self, message) -> None:
        self._send(json.dumps(message))
