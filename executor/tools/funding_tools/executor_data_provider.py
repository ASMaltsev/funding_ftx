from executor.tools.abstract_tools import AbstractExecutorDataProvider


class ExecutorDataProvider(AbstractExecutorDataProvider):

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, secret_key)

    def get_max_limit(self):
        pass

    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool):
        pass

    def make_market_order(self, ticker: str, side: str, quantity: float):
        pass

    def cancel_all_orders(self, ticker: str):
        pass

    def cancel_order(self, ticker: str, order_id: int):
        pass

    def get_positions(self, ticker: str):
        pass

    def get_bbid_bask(self, ticker: str):
        pass

    def get_order_status(self, ticker: str):
        pass
