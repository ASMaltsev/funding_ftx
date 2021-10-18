from strategy.tools.abstract_tools.abstract_executor import AbstractExecutor
from strategy.tools.funding_tools.data_provider_funding import DataProviderFunding
from connectors import ConnectorRouter

import logging
from my_logger import Logger


class FundingExecutor(AbstractExecutor):
    """Funding Executor"""

    def __init__(self, client, data_provider):
        self.client = client
        self.data_provider = data_provider

    def make_market_order(self, ticker: str, side: str, quantity: float, **kwargs) -> dict:
        return self.client.make_market_order(ticker, side, quantity)

    def make_limit_order(self, ticker: str, side: str, price: float, quantity: float, reduce_only: bool, **kwargs) -> dict:
        return self.client.make_limit_order(ticker, side, price, quantity, reduce_only)

    def check_positions(self, data_provider, ticker_swap, ticker_futures):
        pos_swap = self.data_provider.get_positions(ticker_swap)[0]['positionAmt']
        pos_futures = self.data_provider.get_positions(ticker_futures)[0]['positionAmt']

        print(pos_swap, pos_futures)

    def _make_limit_order(self, limit_ticker, side_price, limit_ticker_side, limit_amount, reduce_only, logger) -> tuple:
        """
        place a limit order at the best price
        @return: orderId
        """
        response = None
        price = 0
        order_status = {'status': ''}
        while response is None and order_status['status'] != 'NEW' and order_status['status'] != 'FILLED':
            price = float(self.data_provider.get_bbid_bask(ticker=limit_ticker)[side_price])
            response = self.make_limit_order(ticker=limit_ticker, side=limit_ticker_side,
                                             price=price, quantity=limit_amount,
                                             reduce_only=reduce_only)
            logger.debug(f'Limit order response = {response}')

            order_status = self.data_provider.status_order(ticker=limit_ticker, order_id=response['orderId'])
            logger.debug(f'Limit order status response = {order_status}')

        return price, order_status['orderId']

    def _make_market_order(self, executed_qty, prev_executed_qty, current_amount, logger, market_ticker, market_ticker_side):
        delta = round(float(executed_qty) - prev_executed_qty, 6)
        logger.debug(
            f'Market order: executedQty={executed_qty}, delta={delta}, prev_executedQty={prev_executed_qty}')

        prev_executed_qty = float(executed_qty)
        if delta > 0:
            logger.debug(f'Make market order on {delta}')
            current_amount += delta
            self.make_market_order(ticker=market_ticker,
                                   side=market_ticker_side,
                                   quantity=delta)
        return prev_executed_qty, current_amount



    def execute(self, actions: dict):

        limit_ticker = list(actions.keys())[0]
        market_ticker = list(actions.keys())[1]

        total_amount = actions[limit_ticker]

        if total_amount < 0:
            limit_ticker_side = 'sell'
            market_ticker_side = 'buy'
            reduce_only = False
        else:
             limit_ticker_side = 'buy'
             market_ticker_side = 'sell'
             reduce_only = True

        limit_amount = 0.01
        total_amount = abs(total_amount)


        _logger_name = f'FastStrategyLog_{market_ticker}_{limit_ticker}'
        Logger().create(_logger_name)  # change logging style
        logger = logging.getLogger(_logger_name)  # initial logger

        side_price = None
        if limit_ticker_side.lower() == 'sell':
            side_price = 'askPrice'
        elif limit_ticker_side.lower() == 'buy':
            side_price = 'bidPrice'
        else:
            raise Exception(f'Incorrect limit type {limit_ticker_side}')
        logger.debug(f"""Initial params: market_ticker={market_ticker}, market_ticker_side = {market_ticker_side},
                        limit_ticker = {limit_ticker},  limit_ticker_side = {limit_ticker_side},
                        limit_amount = {limit_amount}, total_amount = {total_amount}, reduce_only = {reduce_only},
                        side_price={side_price}""")



        logger.info('Start execution')
        limit_order_price, order_id = self._make_limit_order(limit_ticker, side_price,
                                                             limit_ticker_side, limit_amount,
                                                             reduce_only, logger)
        prev_executed_qty, current_amount = 0, 0
        while True:
            order_status = self.data_provider.status_order(ticker=limit_ticker, order_id=order_id)
            logger.debug(f'Order status = {order_status}')
            if order_status['status'] == 'FILLED':
                prev_executed_qty, current_amount = self._make_market_order(
                    executed_qty=float(order_status['executedQty']),
                    prev_executed_qty=prev_executed_qty,
                    current_amount=current_amount,
                    logger=logger, market_ticker=market_ticker, market_ticker_side=market_ticker_side)
                prev_executed_qty = 0
                limit_amount = round(min(limit_amount, total_amount - current_amount), 5)
                logger.debug(f'Update limit amount = {limit_amount}')
                if limit_amount == 0:
                    break
                else:
                    limit_order_price, order_id = self._make_limit_order(limit_ticker, side_price,
                                                                         limit_ticker_side, limit_amount,
                                                                         reduce_only, logger)
            elif order_status['status'] == 'EXPIRED':
                limit_amount = round(min(limit_amount, total_amount - current_amount), 5)
                logger.debug(f'Update limit amount = {limit_amount}')
                if limit_amount == 0:
                    break
                else:
                    limit_order_price, order_id = self._make_limit_order(limit_ticker, side_price,
                                                                         limit_ticker_side, limit_amount,
                                                                         reduce_only, logger)
            elif order_status['status'] == 'NEW' or order_status['status'] == 'PARTIALLY_FILLED':

                if order_status['status'] == 'PARTIALLY_FILLED':
                    prev_executed_qty, current_amount = self._make_market_order(
                        executed_qty=float(order_status['executedQty']),
                        prev_executed_qty=prev_executed_qty,
                        current_amount=current_amount,
                        logger=logger, market_ticker=market_ticker, market_ticker_side=market_ticker_side)

                if limit_order_price != float(self.data_provider.get_bbid_bask(ticker=limit_ticker)[side_price]):
                    try:
                        order_status = self.client.cancel_order(ticker=limit_ticker, order_id=order_id) #### !!!!
                    except:
                        order_status = None

                    logger.debug(f'Cancel order status = {order_status}')
                    if order_status is None:
                        prev_executed_qty, current_amount = self._make_market_order(executed_qty=self.limit_amount,
                                                                                    prev_executed_qty=prev_executed_qty,
                                                                                    current_amount=current_amount,
                                                                                    logger=logger, market_ticker=market_ticker,
                                                                                     market_ticker_side=market_ticker_side)
                    else:
                        prev_executed_qty, current_amount = self._make_market_order(
                            executed_qty=order_status['executedQty'],
                            prev_executed_qty=prev_executed_qty,
                            current_amount=current_amount,
                            logger=logger, market_ticker=market_ticker, market_ticker_side=market_ticker_side)
                    limit_amount = round(min(limit_amount, total_amount - current_amount), 5)
                    logger.debug(f'Update limit amount = {limit_amount}')
                    prev_executed_qty = 0
                    if limit_amount == 0:
                        break
                    else:
                        limit_order_price, order_id = self._make_limit_order(limit_ticker, side_price,
                                                                             limit_ticker_side, limit_amount,
                                                                             reduce_only, logger)

            self.check_positions(data_provider=self.data_provider, ticker_swap=limit_ticker,
                                 ticker_futures=market_ticker)
        self.check_positions(data_provider=self.data_provider, ticker_swap=limit_ticker,
                             ticker_futures=market_ticker)
