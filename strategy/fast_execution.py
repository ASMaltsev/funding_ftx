import logging
from my_logger import Logger
from tools.funding_tools.data_provider_funding import DataProviderFunding



class FastStrategy:

    def __init__(self, client, data_provider, market_ticker: str, limit_ticker: str,
                 market_ticker_side: str, limit_ticker_side: str, reduce_only: bool,
                 limit_amount: float, total_amount: float):
        _logger_name = f'FastStrategyLog_{market_ticker}_{limit_ticker}'
        Logger().create(_logger_name)  # change logging style
        self.logger = logging.getLogger(_logger_name)  # initial logger


        self.client = client

        self.data_provider = data_provider

        self.market_ticker = market_ticker
        self.limit_ticker = limit_ticker

        self.market_ticker_side = market_ticker_side
        self.limit_ticker_side = limit_ticker_side

        self.limit_amount = limit_amount
        self.total_amount = total_amount

        self.reduce_only = reduce_only

        self.side_price = None
        if self.limit_ticker_side.lower() == 'sell':
            self.side_price = 'askPrice'
        elif self.limit_ticker_side.lower() == 'buy':
            self.side_price = 'bidPrice'
        else:
            raise Exception(f'Incorrect limit type {limit_ticker_side}')
        self.logger.debug(f"""Initial params: market_ticker={market_ticker}, market_ticker_side = {market_ticker_side},
                        limit_ticker = {limit_ticker},  limit_ticker_side = {limit_ticker_side},
                        limit_amount = {limit_amount}, total_amount = {total_amount}, reduce_only = {reduce_only},
                        side_price={self.side_price}""")

    def check_positions(self, data_provider, ticker_swap, ticker_futures):
        pos_swap = data_provider.get_positions(ticker_swap)[0]['positionAmt']
        pos_futures = data_provider.get_positions(ticker_futures)[0]['positionAmt']

        print(pos_swap, pos_futures)

    def _make_limit_order(self) -> tuple:
        """
        place a limit order at the best price
        @return: orderId
        """
        response = None
        price = 0
        order_status = {'status': ''}
        while response is None and order_status['status'] != 'NEW' and order_status['status'] != 'FILLED':
            price = float(self.data_provider.get_bbid_bask(ticker=self.limit_ticker)[self.side_price])
            response = self.client.make_limit_order(ticker=self.limit_ticker, side=self.limit_ticker_side,
                                                    price=price, quantity=self.limit_amount,
                                                    reduce_only=self.reduce_only)
            self.logger.debug(f'Limit order response = {response}')

            order_status = self.data_provider.status_order(ticker=self.limit_ticker, order_id=response['orderId'])
            self.logger.debug(f'Limit order status response = {order_status}')

        return price, order_status['orderId']

    def _make_market_order(self, executed_qty, prev_executed_qty, current_amount):
        delta = round(float(executed_qty) - prev_executed_qty, 6)
        self.logger.debug(
            f'Market order: executedQty={executed_qty}, delta={delta}, prev_executedQty={prev_executed_qty}')

        prev_executed_qty = float(executed_qty)
        if delta > 0:
            self.logger.debug(f'Make market order on {delta}')
            current_amount += delta
            self.client.make_market_order(ticker=self.market_ticker,
                                          side=self.market_ticker_side,
                                          quantity=delta)
        return prev_executed_qty, current_amount

    def set_position(self):
        self.logger.info('Start execution')
        limit_order_price, order_id = self._make_limit_order()
        prev_executed_qty, current_amount = 0, 0
        while True:
            order_status = self.data_provider.status_order(ticker=self.limit_ticker, order_id=order_id)
            self.logger.debug(f'Order status = {order_status}')
            if order_status['status'] == 'FILLED':
                prev_executed_qty, current_amount = self._make_market_order(
                    executed_qty=float(order_status['executedQty']),
                    prev_executed_qty=prev_executed_qty,
                    current_amount=current_amount)
                prev_executed_qty = 0
                self.limit_amount = round(min(self.limit_amount, self.total_amount - current_amount), 5)
                self.logger.debug(f'Update limit amount = {self.limit_amount}')
                if self.limit_amount == 0:
                    break
                else:
                    limit_order_price, order_id = self._make_limit_order()
            elif order_status['status'] == 'EXPIRED':
                self.limit_amount = round(min(self.limit_amount, self.total_amount - current_amount), 5)
                self.logger.debug(f'Update limit amount = {self.limit_amount}')
                if self.limit_amount == 0:
                    break
                else:
                    limit_order_price, order_id = self._make_limit_order()
            elif order_status['status'] == 'NEW' or order_status['status'] == 'PARTIALLY_FILLED':

                if order_status['status'] == 'PARTIALLY_FILLED':
                    prev_executed_qty, current_amount = self._make_market_order(
                        executed_qty=float(order_status['executedQty']),
                        prev_executed_qty=prev_executed_qty,
                        current_amount=current_amount)

                if limit_order_price != float(self.data_provider.get_bbid_bask(ticker=self.limit_ticker)[self.side_price]):
                    try:
                        order_status = self.client.cancel_order(ticker=self.limit_ticker, order_id=order_id) #### !!!!
                    except:
                        order_status = None

                    self.logger.debug(f'Cancel order status = {order_status}')
                    if order_status is None:
                        prev_executed_qty, current_amount = self._make_market_order(executed_qty=self.limit_amount,
                                                                                    prev_executed_qty=prev_executed_qty,
                                                                                    current_amount=current_amount)
                    else:
                        prev_executed_qty, current_amount = self._make_market_order(
                            executed_qty=order_status['executedQty'],
                            prev_executed_qty=prev_executed_qty,
                            current_amount=current_amount)
                    self.limit_amount = round(min(self.limit_amount, self.total_amount - current_amount), 5)
                    self.logger.debug(f'Update limit amount = {self.limit_amount}')
                    prev_executed_qty = 0
                    if self.limit_amount == 0:
                        break
                    else:
                        limit_order_price, order_id = self._make_limit_order()

            self.check_positions(data_provider=self.data_provider, ticker_swap=self.limit_ticker,
                                 ticker_futures=self.market_ticker)
        self.check_positions(data_provider=self.data_provider, ticker_swap=self.limit_ticker,
                             ticker_futures=self.market_ticker)
