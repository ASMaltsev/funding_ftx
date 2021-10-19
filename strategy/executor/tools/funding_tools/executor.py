import time
import sys
from strategy.executor.tools.abstract_tools.abstract_executor import AbstractExecutor
from strategy.executor.tools.funding_tools.parser_actions import ParserActions
from strategy.executor.tools.funding_tools.binance_data_provider import BinanceDataProvider
from strategy.others import Logger

logger = Logger('Executor').create()


class FundingExecutor(AbstractExecutor):

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, secret_key)
        self.data_provider = BinanceDataProvider(api_key, secret_key, 'USDT-M')
        self.start_amount_limit = 0
        self.start_amount_market = 0

    def execute(self, actions: dict) -> bool:
        logger.info(msg='Executor is starting.')
        # parser = ParserActions(actions)
        # actions_for_execute = parser.parse()
        ticker_swap = 'ETHUSDT'
        ticker_futures = 'ETHUSDT_211231'

        swap_side = 'buy'
        futures_side = 'sell'
        reduce_only = True
        total_amount = 0.08

        self._execute(
            market_ticker=ticker_futures,
            market_side=futures_side,
            limit_ticker=ticker_swap,
            limit_side=swap_side,
            reduce_only=reduce_only,
            total_amount=total_amount)

        return True

    def check_positions(self, limit_ticker, market_ticker, market_ticker_side):
        self.data_provider.cancel_all_orders(limit_ticker)
        self.data_provider.cancel_all_orders(market_ticker)
        pos_limit_side = self.data_provider.get_amount_positions(limit_ticker)
        pos_market_side = self.data_provider.get_amount_positions(market_ticker)

        logger.info(msg='Control positions.',
                    extra=dict(pos_market_side=pos_market_side, pos_limit_side=pos_limit_side))

        current_position_limit = round(pos_limit_side - self.start_amount_limit, 5)
        current_position_market = round(pos_market_side - self.start_amount_market, 5)

        delta = round(abs(current_position_limit) - abs(current_position_market), 4)
        logger.info(msg=f'CHECK POSITION.', extra=dict(delta=delta))
        limit_amount = self._get_limit_amount(limit_ticker)
        if 0 < delta <= limit_amount:
            self.data_provider.make_safety_market_order(ticker=market_ticker,
                                                        side=market_ticker_side,
                                                        quantity=delta)
        elif delta < 0 and abs(delta) <= limit_amount:
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

    def _get_limit_amount(self, ticker: str) -> float:
        """
        @param ticker: pair name
        @return: amount for one limit order
        """
        if ticker.startswith('BTC'):
            return 0.002
        if ticker.startswith('ETH'):
            return 0.03
        raise NotImplementedError

    def _execute(self, market_ticker: str, limit_ticker: str, limit_side: str, market_side: str,
                 total_amount: float, reduce_only: bool) -> bool:

        logger.info(msg='Start shopping.',
                    extra=dict(market_ticker=market_ticker, market_side=market_side, limit_ticker=limit_ticker,
                               limit_side=limit_side, total_amount=total_amount, reduce_only=reduce_only))

        current_amount_qty, prev_executed_qty = 0, 0
        min_size_market_order = self.data_provider.min_size_for_market_order(ticker=market_ticker)

        precision = abs(str(min_size_market_order).find('.') - len(str(min_size_market_order))) + 1
        limit_qty = round(min(self._get_limit_amount(ticker=limit_ticker), total_amount - current_amount_qty),
                          precision)

        order_status, order_id, price_limit_order, executed_qty = self.data_provider.make_safety_limit_order(
            ticker=limit_ticker,
            side=limit_side,
            quantity=limit_qty,
            reduce_only=reduce_only)

        while True:

            logger.debug(msg='Order status for limit order.',
                         extra=dict(order_id=order_id, order_status=order_status, executed_qty=executed_qty))

            logger.info(msg='Current position.', extra=dict(current_amount_qty=current_amount_qty))

            delta = executed_qty - prev_executed_qty
            prev_executed_qty = executed_qty

            if order_status == 'FILLED':
                logger.debug(msg='Make market order.', extra=dict(ticker=market_ticker, quantity=delta))
                self.data_provider.make_safety_market_order(ticker=market_ticker, side=market_side,
                                                            quantity=delta,
                                                            min_size_order=min_size_market_order)
                current_amount_qty += delta
                limit_qty = round(min(self._get_limit_amount(ticker=limit_ticker), total_amount - current_amount_qty),
                                  precision)

                if limit_qty == 0:
                    self.check_positions(limit_ticker=limit_ticker, market_ticker=market_ticker,
                                         market_ticker_side=market_side)
                    logger.info(msg='Finished.')
                    break

                self._control_rpc()
                order_status, order_id, price_limit_order, executed_qty = self.data_provider.make_safety_limit_order(
                    ticker=limit_ticker,
                    side=limit_side,
                    quantity=limit_qty,
                    reduce_only=reduce_only)
            elif order_status == 'PARTIALLY_FILLED' or order_status == 'NEW':

                if order_status == 'PARTIALLY_FILLED':
                    logger.debug(msg='Make market order', extra=dict(ticker=market_ticker, quantity=delta))
                    self.data_provider.make_safety_market_order(ticker=market_ticker, side=market_side,
                                                                quantity=delta,
                                                                min_size_order=min_size_market_order)
                    current_amount_qty += delta

                side_index = 0 if limit_side == 'sell' else 1
                current_price = self.data_provider.get_bbid_bask(ticker=limit_ticker)[side_index]

                if price_limit_order != current_price:
                    is_cancel = self.data_provider.cancel_order(ticker=limit_ticker,
                                                                order_id=order_id)
                    order_status, executed_qty = self.data_provider.get_order_status(ticker=limit_ticker,
                                                                                     order_id=order_id)
                    delta = executed_qty - prev_executed_qty
                    logger.debug(msg='Params canceled orders',
                                 extra=dict(order_status=order_status, executed_qty=executed_qty, delta=delta,
                                            is_cancel=is_cancel, order_id=order_id))
                    if is_cancel:
                        logger.debug(msg='Make market order', extra=dict(ticker=market_ticker, quantity=delta))
                        self.data_provider.make_safety_market_order(ticker=market_ticker,
                                                                    side=market_side,
                                                                    quantity=delta,
                                                                    min_size_order=min_size_market_order)
                        current_amount_qty += delta
                        limit_qty = round(
                            min(self._get_limit_amount(ticker=limit_ticker), total_amount - current_amount_qty),
                            precision)
                        if limit_qty == 0:
                            self.check_positions(limit_ticker=limit_ticker, market_ticker=market_ticker,
                                                 market_ticker_side=market_side)
                            logger.info(msg='Finished.')
                            break

                        self._control_rpc()
                        order_status, order_id, price_limit_order, executed_qty = \
                            self.data_provider.make_safety_limit_order(ticker=limit_ticker, side=limit_side,
                                                                       quantity=limit_qty, reduce_only=reduce_only)
        return True
