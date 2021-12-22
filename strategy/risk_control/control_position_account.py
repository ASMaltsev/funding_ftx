from strategy.data_provider import BinanceDataProvider
from strategy.logging import Logger
from strategy.risk_control import TelegramBot
from strategy.executor.binance_executor.executor import BinanceExecutor

logger = Logger('AccountControl').create()


class AccountPosition:

    def __init__(self, provider_usdt_m: BinanceDataProvider, provider_coin_m: BinanceDataProvider,
                 provider_hyperparams):
        self.dict_provider = {'USDT-M': provider_usdt_m, 'COIN-M': provider_coin_m}
        self.provider_hyperparams = provider_hyperparams

    @staticmethod
    def _rebalance(provider, ticker, delta, precision, side):

        min_size_order = provider.min_size_for_market_order(ticker)

        logger.info('Account rebalance params', extra=dict(ticker=ticker, side=side, quantity=delta,
                                                           min_size_order=min_size_order,
                                                           precision=precision))

        provider.make_safety_market_order(ticker=ticker, side=side, quantity=delta,
                                          min_size_order=min_size_order,
                                          precision=precision)

    def control(self, strategy_section):
        bot = TelegramBot()
        max_coef_delta = 1.2
        sections = self.provider_hyperparams.get_sections()
        section = 'USDT-M'
        if section in sections:
            provider = self.dict_provider[section]
            assets = self.provider_hyperparams.get_assets(section)
            for asset in assets:
                perp = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='perp')
                quart = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='quart')
                limit_amount = self.provider_hyperparams.get_limit_amount(section=section, asset=asset)
                provider.cancel_all_orders(perp)
                provider.cancel_all_orders(quart)

                precision = BinanceExecutor.get_precision(perp)

                pos_perp = round(provider.get_amount_positions(perp), precision)
                pos_quart = round(provider.get_amount_positions(quart), precision)
                logger.info('Positions: ', extra=dict(pos_perp=pos_perp, pos_quart=pos_quart))

                delta = abs(round(pos_perp + pos_quart, precision))
                logger.info(msg=f'Delta: ', extra=dict(delta=delta))
                if 0 < delta <= max_coef_delta * limit_amount:
                    bot.send_message(
                        msg=f'Bad positions. USDT-M. [{perp}: {pos_perp}, {quart}: {pos_quart}, delta: {delta}]')
                    if abs(pos_quart) < abs(pos_perp):
                        if strategy_section == 'setup':
                            self._rebalance(provider=provider, ticker=quart, delta=delta,
                                            precision=precision, side='buy')

                        elif strategy_section == 'exit':
                            self._rebalance(provider=provider, ticker=perp, delta=delta,
                                            precision=precision, side='sell')

                    else:
                        if strategy_section == 'setup':
                            self._rebalance(provider=provider, ticker=perp, delta=delta,
                                            precision=precision, side='buy')

                        elif strategy_section == 'exit':
                            self._rebalance(provider=provider, ticker=quart, delta=delta,
                                            precision=precision, side='sell')

                elif delta > 0 and delta > max_coef_delta * limit_amount:
                    bot.send_message(
                        msg=f"""Stop run. Very bad positions. USDT-M. [{perp}: {pos_perp}, 
                                                                        {quart}: {pos_quart}, {delta}: {delta}]""")
                    logger.error(msg='Very bad positions',
                                 extra=dict(perp=perp, pos_perp=pos_perp, quart=quart, pos_quart=pos_quart))
                    exit(0)

        section = 'COIN-M'
        if section in sections:

            provider = self.dict_provider[section]
            assets = self.provider_hyperparams.get_assets(section)

            precision = 0
            for asset in assets:
                perp_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='perp')
                current_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset,
                                                                               kind='current')
                next_ticker = self.provider_hyperparams.get_ticker_by_asset(section=section, asset=asset, kind='next')

                provider.cancel_all_orders(perp_ticker)
                provider.cancel_all_orders(next_ticker)
                provider.cancel_all_orders(current_ticker)

                pos_perp = round(provider.get_amount_positions(perp_ticker), precision)
                pos_cur = round(provider.get_amount_positions(current_ticker), precision)
                pos_next = round(provider.get_amount_positions(next_ticker), precision)
                limit_amount = self.provider_hyperparams.get_limit_amount(section=section, asset=asset)

                logger.info('Positions: ', extra=dict(pos_perp=pos_perp, pos_cur=pos_cur, pos_next=pos_next))

                delta = abs(round(pos_perp + pos_next + pos_cur, precision))

                logger.info(msg=f'Delta: ', extra=dict(delta=delta))
                if 0 < delta <= max_coef_delta * limit_amount:
                    bot.send_message(
                        msg=f"""Bad positions. COIN-M. [{perp_ticker}: {pos_perp}, {current_ticker}: {pos_cur},
                                                            {next_ticker}: {pos_next}]""")
                    if abs(pos_cur + pos_next) < abs(pos_perp):
                        if strategy_section == 'setup':
                            self._rebalance(provider=provider, ticker=next_ticker, delta=delta,
                                            precision=precision, side='buy')

                        elif strategy_section == 'exit':
                            self._rebalance(provider=provider, ticker=perp_ticker, delta=delta,
                                            precision=precision, side='sell')

                    else:
                        if strategy_section == 'setup':
                            self._rebalance(provider=provider, ticker=perp_ticker, delta=delta,
                                            precision=precision, side='buy')

                        elif strategy_section == 'exit':
                            self._rebalance(provider=provider, ticker=current_ticker, delta=delta,
                                            precision=precision, side='sell')

                elif delta > 0 and delta > max_coef_delta * limit_amount:
                    bot.send_message(
                        msg=f"""Stop run. Very bad positions. COIN-M. [{perp_ticker}: {pos_perp}, {current_ticker}: {pos_cur},
                    {next_ticker}, {pos_next}]""")
                    logger.error(msg='Very bad positions',
                                 extra=dict(perp_ticker=perp_ticker, pos_perp=pos_perp, current_ticker=current_ticker,
                                            pos_cur=pos_cur, next_ticker=next_ticker, pos_next=pos_next))
                    exit(0)
