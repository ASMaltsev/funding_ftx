from strategy.data_provider import BinanceDataProvider
from strategy.hyperparams import ProviderHyperParamsStrategy
from strategy.logging import Logger
from strategy.executor.binance_executor.executor import BinanceExecutor
from strategy.risk_control import TelegramBot

logger = Logger('AccountControl').create()


class AccountPosition:

    def __init__(self, provider_usdt_m: BinanceDataProvider, provider_coin_m: BinanceDataProvider):
        self.dict_provider = {'USDT-M': provider_usdt_m, 'COIN-M': provider_coin_m}
        self.provider_hp = ProviderHyperParamsStrategy()

    @staticmethod
    def _rebalance(position, provider, ticker, delta):
        side = 'buy' if position < 0 else 'sell'
        min_size_order = provider.min_size_for_market_order(ticker)
        provider.make_safety_market_order(ticker=ticker, side=side, quantity=delta,
                                          min_size_order=min_size_order)

    def control(self):
        bot = TelegramBot()
        max_coef_delta = 1.2
        sections = self.provider_hp.get_sections()
        section = 'USDT-M'
        if section in sections:
            provider = self.dict_provider[section]
            assets = self.provider_hp.get_assets(section)
            precision = 4
            for asset in assets:
                perp = self.provider_hp.get_ticker_by_asset(section=section, asset=asset, kind='perp')
                quart = self.provider_hp.get_ticker_by_asset(section=section, asset=asset, kind='quart')
                provider.cancel_all_orders(perp)
                provider.cancel_all_orders(quart)

                pos_perp = round(provider.get_amount_positions(perp), precision)
                pos_quart = round(provider.get_amount_positions(quart), precision)
                logger.info('Positions: ', extra=dict(pos_perp=pos_perp, pos_quart=pos_quart))

                delta = abs(round(pos_perp + pos_quart, precision))
                logger.info(msg=f'Delta: ', extra=dict(delta=delta))
                if 0 < delta <= max_coef_delta * BinanceExecutor.get_limit_amount(perp):
                    bot.send_message(msg=f'Bad positions. USDT-M. [{perp}: {pos_perp}, {quart}: {pos_quart}]')
                    if abs(pos_perp) < abs(pos_quart):
                        self._rebalance(position=pos_quart, provider=provider, ticker=quart, delta=delta)
                    else:
                        self._rebalance(position=pos_perp, provider=provider, ticker=perp, delta=delta)
                elif delta > 0 and delta > max_coef_delta * BinanceExecutor.get_limit_amount(perp):
                    bot.send_message(msg=f'Stop run. Very bad positions. USDT-M. [{perp}: {pos_perp},'
                                         f' {quart}: {pos_quart}]')
                    logger.error(msg='Very bad positions',
                                 extra=dict(perp=perp, pos_perp=pos_perp, quart=quart, pos_quart=pos_quart))
                    exit(0)

        section = 'COIN-M'
        if section in sections:

            provider = self.dict_provider[section]
            assets = self.provider_hp.get_assets(section)

            precision = 0
            for asset in assets:
                perp_ticker = self.provider_hp.get_ticker_by_asset(section=section, asset=asset, kind='perp')
                current_ticker = self.provider_hp.get_ticker_by_asset(section=section, asset=asset, kind='current')
                next_ticker = self.provider_hp.get_ticker_by_asset(section=section, asset=asset, kind='next')

                provider.cancel_all_orders(perp_ticker)
                provider.cancel_all_orders(next_ticker)
                provider.cancel_all_orders(current_ticker)

                pos_perp = round(provider.get_amount_positions(perp_ticker), precision)
                pos_cur = round(provider.get_amount_positions(current_ticker), precision)
                pos_next = round(provider.get_amount_positions(next_ticker), precision)

                logger.info('Positions: ', extra=dict(pos_perp=pos_perp, pos_cur=pos_cur, pos_next=pos_next))

                delta = abs(round(pos_perp + pos_next + pos_cur, precision))

                logger.info(msg=f'Delta: ', extra=dict(delta=delta))
                if 0 < delta <= max_coef_delta * BinanceExecutor.get_limit_amount(perp_ticker):
                    bot.send_message(
                        msg=f"""Bad positions. USDT-M. [{perp_ticker}: {pos_perp}, {current_ticker}: {pos_cur},'
                                                            {next_ticker}, {pos_next}]""")
                    if abs(pos_cur + pos_next) < abs(pos_perp):
                        self._rebalance(position=pos_perp, provider=provider, ticker=perp_ticker, delta=delta)
                    else:
                        if abs(pos_cur) < abs(pos_next):
                            self._rebalance(position=pos_next, provider=provider, ticker=next_ticker, delta=delta)
                        else:
                            self._rebalance(position=pos_cur, provider=provider, ticker=current_ticker, delta=delta)
