import time
import sys
import requests
from strategy.executor.abstract_executor import AbstractExecutor
from strategy.data_provider import FtxDataProvider
from strategy.logging import Logger, send_log

my_logger = Logger('Executor')
logger = my_logger.create()


class FtxExecutor(AbstractExecutor):

    def __init__(self, api_key: str, secret_key: str, market_ticker: str, limit_ticker: str,
                 limit_side: str, market_side: str, total_amount: float, reduce_only: bool, limit_amount: float):

        self.data_provider = FtxDataProvider(api_key=api_key, secret_key=secret_key)

        self.limit_amount = limit_amount
        self.start_amount_limit = 0
        self.start_amount_market = 0
        self.market_ticker = market_ticker
        self.limit_ticker = limit_ticker
        self.limit_side = limit_side
        self.market_side = market_side
        self.total_amount = total_amount
        self.reduce_only = reduce_only
        self.current_amount_qty = 0
        self.precision = 3

    def check_positions(self, min_size_order):
        max_coef_delta = 1.2
        time.sleep(0.1)

        pos_limit_side, pos_market_side = 0, 0
        for _ in range(3):
            pos_limit_side = round(self.data_provider.get_amount_positions(self.limit_ticker), self.precision)
            pos_market_side = round(self.data_provider.get_amount_positions(self.market_ticker), self.precision)

        logger.info(msg='Control positions.',
                    extra=dict(pos_market_side=pos_market_side, pos_limit_side=pos_limit_side))

        current_position_limit = round(pos_limit_side - self.start_amount_limit, self.precision)
        current_position_market = round(pos_market_side - self.start_amount_market, self.precision)

        delta = round(abs(current_position_limit) - abs(current_position_market), self.precision)
        logger.info(msg=f'CHECK POSITION.', extra=dict(delta=delta))
        if 0 < delta <= max_coef_delta * self.limit_amount:
            self.data_provider.make_safety_market_order(ticker=self.market_ticker,
                                                        side=self.market_side,
                                                        quantity=delta,
                                                        min_size_order=min_size_order,
                                                        precision=self.precision)
        elif delta < 0 and abs(delta) <= max_coef_delta * self.limit_amount:
            self.data_provider.make_safety_market_order(ticker=self.market_ticker,
                                                        side=self.market_side,
                                                        quantity=abs(delta),
                                                        min_size_order=min_size_order,
                                                        precision=self.precision)
        elif delta == 0:
            pass
        else:
            logger.error(msg="REBALANCE FALSE")
            sys.exit(0)

    def _log_current_positions(self, min_size_order):
        time.sleep(0.2)
        limit_amount = self.data_provider.get_amount_positions(self.limit_ticker)
        market_amount = self.data_provider.get_amount_positions(self.market_ticker)
        logger.info(msg='Current positions:',
                    extra=dict(limit_amount=limit_amount, market_amount=market_amount,
                               delta=limit_amount + market_amount))
        delta = abs((limit_amount - self.start_amount_limit) + (market_amount - self.start_amount_market))
        logger.info(msg='Current positions with correction on initial positions:',
                    extra=dict(limit_amount=limit_amount - self.start_amount_limit,
                               market_amount=market_amount - self.start_amount_market,
                               delta=delta))
        if delta > 0:
            logger.error(msg='Delta positions > 0. Stopped.', extra=dict(delta=delta))
            self.check_positions(min_size_order)

    def execute(self) -> bool:
        try:
            self.start_amount_limit = 0
            self.start_amount_market = 0

            prev_executed_qty = 0
            min_size_market_order = self.data_provider.min_size_for_market_order(ticker=self.market_ticker)
            self.check_positions(self.data_provider.min_size_for_market_order(min_size_market_order))

            limit_qty = round(
                min(self.limit_amount, self.total_amount - self.current_amount_qty),
                self.precision)

            logger.info(msg='Start shopping.',
                        extra=dict(market_ticker=self.market_ticker, market_side=self.market_side,
                                   limit_ticker=self.limit_ticker,
                                   limit_side=self.limit_side, total_amount=self.total_amount,
                                   reduce_only=self.reduce_only,
                                   start_amount_limit=self.start_amount_limit,
                                   start_amount_market=self.start_amount_market, precision=self.precision,
                                   limit_amount=self.limit_amount))

            order_status, order_id, price_limit_order, executed_qty = self.data_provider.make_safety_limit_order(
                ticker=self.limit_ticker,
                side=self.limit_side,
                quantity=limit_qty,
                reduce_only=self.reduce_only)


            while True:

                delta = round(executed_qty - prev_executed_qty, self.precision)
                prev_executed_qty = executed_qty

                if order_status == 'FILLED':
                    logger.info(msg='Make market order.', extra=dict(ticker=self.market_ticker, quantity=delta))
                    self.data_provider.make_safety_market_order(ticker=self.market_ticker, side=self.market_side,
                                                                quantity=delta,
                                                                min_size_order=min_size_market_order,
                                                                precision=self.precision)
                    self.current_amount_qty += delta
                    limit_qty = round(min(self.limit_amount,
                                          self.total_amount - self.current_amount_qty),
                                      self.precision)

                    if limit_qty == 0:
                        self.check_positions(min_size_market_order)
                        logger.info(msg='Finished.')
                        break

                    prev_executed_qty = 0

                    order_status, order_id, price_limit_order, executed_qty = self.data_provider. \
                        make_safety_limit_order(ticker=self.limit_ticker,
                                                side=self.limit_side,
                                                quantity=limit_qty,
                                                reduce_only=self.reduce_only)
                    logger.info(msg='Current position.', extra=dict(current_amount_qty=self.current_amount_qty))

                elif order_status == 'PARTIALLY_FILLED' or order_status == 'NEW':

                    if order_status == 'PARTIALLY_FILLED':
                        logger.info(msg='Make market order', extra=dict(ticker=self.market_ticker, quantity=delta))
                        self.data_provider.make_safety_market_order(ticker=self.market_ticker, side=self.market_side,
                                                                    quantity=delta,
                                                                    min_size_order=min_size_market_order,
                                                                    precision=self.precision)
                        self.current_amount_qty += delta

                    side_index = 1 if self.limit_side == 'sell' else 0
                    current_price = self.data_provider.get_bbid_bask(ticker=self.limit_ticker)[side_index]

                    if price_limit_order != current_price:
                        is_cancel = self.data_provider.cancel_order(ticker=self.limit_ticker,
                                                                    order_id=order_id)

                        order_status, executed_qty = self.data_provider.get_order_status(ticker=self.limit_ticker,
                                                                                         order_id=order_id)

                        delta = round(executed_qty - prev_executed_qty, self.precision)
                        logger.info(msg='Params canceled orders',
                                    extra=dict(order_status=order_status, executed_qty=executed_qty, delta=delta,
                                               is_cancel=is_cancel, order_id=order_id))
                        if is_cancel:
                            logger.info(msg='Make market order', extra=dict(ticker=self.market_ticker, quantity=delta))
                            self.data_provider.make_safety_market_order(ticker=self.market_ticker,
                                                                        side=self.market_side,
                                                                        quantity=delta,
                                                                        min_size_order=min_size_market_order,
                                                                        precision=self.precision)
                            self.current_amount_qty += delta
                            limit_qty = round(
                                min(self.limit_amount,
                                    self.total_amount - self.current_amount_qty), self.precision)
                            if limit_qty == 0:
                                self.check_positions(min_size_market_order)
                                logger.info(msg='Finished.')
                                break

                            prev_executed_qty = 0

                            order_status, order_id, price_limit_order, executed_qty = \
                                self.data_provider.make_safety_limit_order(ticker=self.limit_ticker,
                                                                           side=self.limit_side,
                                                                           quantity=limit_qty,
                                                                           reduce_only=self.reduce_only)
                    time.sleep(0.2)
                    order_status, executed_qty = self.data_provider.get_order_status(ticker=self.limit_ticker,
                                                                                     order_id=order_id)
            return True
        except requests.ConnectionError as e:
            logger.error(msg=str(e))
            min_size_market_order = self.data_provider.min_size_for_market_order(ticker=self.market_ticker)
            self.total_amount -= self.current_amount_qty
            self.current_amount_qty = 0
            self.check_positions(min_size_market_order)
            self.execute()

        except Exception as e:
            logger.exception(msg=str(e))
        finally:
            send_log()
