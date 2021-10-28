from termcolor import colored

import time
import sys
from strategy.executor.tools.abstract_tools.abstract_executor import AbstractExecutor
from strategy.others import Logger, send_log

my_logger = Logger('Executor')
logger = my_logger.create()


class FundingExecutor(AbstractExecutor):

    def __init__(self, data_provider):
        super().__init__(data_provider)
        self.start_amount_limit = 0
        self.start_amount_market = 0

    def _work_before_new_limit_order(self, limit_ticker, market_ticker):
        logger.debug(msg=colored('Rate limits:', 'blue'),
                     extra=dict(current_rpc=self.data_provider.current_rpc, max_rpc=self.data_provider.max_rpc))
        self._control_rpc()
        self._log_current_positions(limit_ticker, market_ticker)

    def check_positions(self, limit_ticker, market_ticker, market_ticker_side):
        max_coef_delta = 1.2
        self.data_provider.cancel_all_orders(limit_ticker)
        self.data_provider.cancel_all_orders(market_ticker)
        pos_limit_side = self.data_provider.get_amount_positions(limit_ticker)
        pos_market_side = self.data_provider.get_amount_positions(market_ticker)

        logger.info(msg=colored('Control positions.', 'green'),
                    extra=dict(pos_market_side=pos_market_side, pos_limit_side=pos_limit_side))

        current_position_limit = round(pos_limit_side - self.start_amount_limit, 5)
        current_position_market = round(pos_market_side - self.start_amount_market, 5)

        delta = round(abs(current_position_limit) - abs(current_position_market), 4)
        logger.info(msg=f'CHECK POSITION.', extra=dict(delta=delta))
        limit_amount = self._get_limit_amount(limit_ticker)
        if 0 < delta <= max_coef_delta * limit_amount:
            self.data_provider.make_safety_market_order(ticker=market_ticker,
                                                        side=market_ticker_side,
                                                        quantity=delta)
        elif delta < 0 and abs(delta) <= max_coef_delta * limit_amount:
            self.data_provider.make_safety_market_order(ticker=market_ticker,
                                                        side=market_ticker_side,
                                                        quantity=abs(delta))
        elif delta == 0:
            pass
        else:
            logger.error(msg="REBALANCE FALSE")
            sys.exit(0)

    def _control_rpc(self):
        if self.data_provider.warning_rpc:
            time.sleep(30)

    def _log_current_positions(self, limit_ticker, market_ticker):
        limit_amount = self.data_provider.get_amount_positions(limit_ticker)
        market_amount = self.data_provider.get_amount_positions(market_ticker)
        logger.info(msg=colored('Current positions:', 'green'),
                    extra=dict(limit_amount=limit_amount, market_amount=market_amount,
                               delta=limit_amount + market_amount))
        delta = abs((limit_amount - self.start_amount_limit) + (market_amount - self.start_amount_market))
        logger.info(msg=colored('Current positions with correction on initial positions:', 'green'),
                    extra=dict(limit_amount=limit_amount - self.start_amount_limit,
                               market_amount=market_amount - self.start_amount_market,
                               delta=delta))
        if delta > 0:
            logger.error(msg='Delta positions > 0.Stopped.', extra=dict(delta=delta))
            sys.exit(0)

    def _get_limit_amount(self, ticker: str) -> float:
        """
        @param ticker: pair name
        @return: amount for one limit order
        """
        if ticker.startswith('BTCUSDT'):
            return 0.002
        elif ticker.startswith('ETHUSDT'):
            return 0.03
        elif ticker.startswith('BTCUSD'):
            return 2
        elif ticker.startswith('ETHUSD'):
            return 1
        raise NotImplementedError

    def execute(self, market_ticker: str, limit_ticker: str, limit_side: str, market_side: str,
                total_amount: float, reduce_only: bool) -> bool:
        try:
            self.start_amount_limit = self.data_provider.get_amount_positions(limit_ticker)
            self.start_amount_market = self.data_provider.get_amount_positions(market_ticker)

            current_amount_qty, prev_executed_qty = 0, 0
            min_size_market_order = self.data_provider.min_size_for_market_order(ticker=market_ticker)

            precision = abs(str(min_size_market_order).find('.') - len(str(min_size_market_order))) + 1
            limit_qty = round(
                min(self._get_limit_amount(ticker=limit_ticker), total_amount - current_amount_qty),
                precision)
            logger.info('Sleeping 60 sec for revocation RPC...')
            time.sleep(60)

            logger.info(msg='Start shopping.',
                        extra=dict(market_ticker=market_ticker, market_side=market_side, limit_ticker=limit_ticker,
                                   limit_side=limit_side, total_amount=total_amount, reduce_only=reduce_only,
                                   start_amount_limit=self.start_amount_limit,
                                   start_amount_market=self.start_amount_market, precision=precision))

            self._work_before_new_limit_order(limit_ticker, market_ticker)
            order_status, order_id, price_limit_order, executed_qty = self.data_provider.make_safety_limit_order(
                ticker=limit_ticker,
                side=limit_side,
                quantity=limit_qty,
                reduce_only=reduce_only)

            while True:

                delta = round(executed_qty - prev_executed_qty, precision)
                prev_executed_qty = executed_qty

                if order_status == 'FILLED':
                    logger.info(msg='Make market order.', extra=dict(ticker=market_ticker, quantity=delta))
                    self.data_provider.make_safety_market_order(ticker=market_ticker, side=market_side,
                                                                quantity=delta,
                                                                min_size_order=min_size_market_order)
                    current_amount_qty += delta
                    limit_qty = round(min(self._get_limit_amount(ticker=limit_ticker),
                                          total_amount - current_amount_qty),
                                      precision)

                    if limit_qty == 0:
                        self.check_positions(limit_ticker=limit_ticker, market_ticker=market_ticker,
                                             market_ticker_side=market_side)
                        logger.info(msg='Finished.')
                        break

                    prev_executed_qty = 0

                    self._work_before_new_limit_order(limit_ticker, market_ticker)
                    order_status, order_id, price_limit_order, executed_qty = self.data_provider. \
                        make_safety_limit_order(ticker=limit_ticker,
                                                side=limit_side,
                                                quantity=limit_qty,
                                                reduce_only=reduce_only)
                    logger.info(msg='Current position.', extra=dict(current_amount_qty=current_amount_qty))

                elif order_status == 'PARTIALLY_FILLED' or order_status == 'NEW':

                    if order_status == 'PARTIALLY_FILLED':
                        logger.info(msg='Make market order', extra=dict(ticker=market_ticker, quantity=delta))
                        self.data_provider.make_safety_market_order(ticker=market_ticker, side=market_side,
                                                                    quantity=delta,
                                                                    min_size_order=min_size_market_order)
                        current_amount_qty += delta

                    side_index = 1 if limit_side == 'sell' else 0
                    current_price = self.data_provider.get_bbid_bask(ticker=limit_ticker)[side_index]

                    if price_limit_order != current_price:
                        is_cancel = self.data_provider.cancel_order(ticker=limit_ticker,
                                                                    order_id=order_id)

                        order_status, executed_qty = self.data_provider.get_order_status(ticker=limit_ticker,
                                                                                         order_id=order_id)

                        delta = round(executed_qty - prev_executed_qty, precision)
                        logger.info(msg='Params canceled orders',
                                    extra=dict(order_status=order_status, executed_qty=executed_qty, delta=delta,
                                               is_cancel=is_cancel, order_id=order_id))
                        if is_cancel:
                            logger.info(msg='Make market order', extra=dict(ticker=market_ticker, quantity=delta))
                            self.data_provider.make_safety_market_order(ticker=market_ticker,
                                                                        side=market_side,
                                                                        quantity=delta,
                                                                        min_size_order=min_size_market_order)
                            current_amount_qty += delta
                            limit_qty = round(
                                min(self._get_limit_amount(ticker=limit_ticker),
                                    total_amount - current_amount_qty), precision)
                            if limit_qty == 0:
                                self.check_positions(limit_ticker=limit_ticker, market_ticker=market_ticker,
                                                     market_ticker_side=market_side)
                                logger.info(msg='Finished.')
                                break

                            prev_executed_qty = 0

                            self._work_before_new_limit_order(limit_ticker, market_ticker)
                            order_status, order_id, price_limit_order, executed_qty = \
                                self.data_provider.make_safety_limit_order(ticker=limit_ticker, side=limit_side,
                                                                           quantity=limit_qty, reduce_only=reduce_only)
                    time.sleep(0.2)
                    order_status, executed_qty = self.data_provider.get_order_status(ticker=limit_ticker,
                                                                                     order_id=order_id)
            return True

        except Exception as e:
            logger.error(msg=str(e))
            return False
        finally:
            send_log()
