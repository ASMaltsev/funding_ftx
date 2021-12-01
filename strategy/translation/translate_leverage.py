from strategy.translation import GeneratePosition


class TranslateLeverage:

    def __init__(self, data_provider_usdt_m, data_provider_coin_m, hyperparams_provider):
        self.data_provider_usdt_m = data_provider_usdt_m
        self.data_provider_coin_m = data_provider_coin_m
        self.generate_position = GeneratePosition()
        self.hyperparams_provider = hyperparams_provider

    def translate(self, instructions, strategy_positions):
        update_instructions = []
        sections = self.hyperparams_provider.get_sections()
        section = 'USDT-M'
        if section in sections:
            for asset, close_amount in instructions[section].items():
                perp_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='perp', asset=asset)
                quart_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='quart', asset=asset)

                pos = self.generate_position.get_close_position_instruction(section=section, market_ticker=quart_ticker,
                                                                            limit_ticker=perp_ticker,
                                                                            total_amount=close_amount)
                update_instructions.append(pos)

        section = 'COIN-M'
        if section in sections:
            for asset, close_amount in instructions[section].items():
                perp_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='perp', asset=asset)

                current_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='current',
                                                                               asset=asset)
                next_ticker = self.hyperparams_provider.get_ticker_by_asset(section=section, kind='next', asset=asset)

                amount_current = self.data_provider_coin_m.get_amount_positions(current_ticker)
                amount_next = self.data_provider_coin_m.get_amount_positions(next_ticker)

                strategy_amount_next = strategy_positions[section].get(next_ticker, 0)
                strategy_amount_curr = strategy_positions[section].get(current_ticker, 0)

                if abs(strategy_amount_next) <= abs(strategy_amount_curr) - close_amount:
                    update_instructions.append(
                        self.generate_position.get_close_position_instruction(section=section,
                                                                              market_ticker=current_ticker,
                                                                              limit_ticker=perp_ticker,
                                                                              total_amount=close_amount))
                    update_instructions.append(
                        self.generate_position.get_close_position_instruction(section=section,
                                                                              market_ticker=next_ticker,
                                                                              limit_ticker=perp_ticker,
                                                                              total_amount=0))
                else:
                    if abs(strategy_amount_next) - close_amount >= abs(strategy_amount_curr):
                        update_instructions.append(
                            self.generate_position.get_close_position_instruction(section=section,
                                                                                  market_ticker=current_ticker,
                                                                                  limit_ticker=perp_ticker,
                                                                                  total_amount=0))
                        update_instructions.append(
                            self.generate_position.get_close_position_instruction(section=section,
                                                                                  market_ticker=next_ticker,
                                                                                  limit_ticker=perp_ticker,
                                                                                  total_amount=close_amount))
                    else:
                        try:
                            coef = amount_current / (amount_next + amount_current)
                        except ZeroDivisionError:
                            coef = 0.5

                        update_instructions.append(
                            self.generate_position.get_close_position_instruction(section=section,
                                                                                  market_ticker=current_ticker,
                                                                                  limit_ticker=perp_ticker,
                                                                                  total_amount=round(
                                                                                      coef * close_amount)))

                        update_instructions.append(
                            self.generate_position.get_close_position_instruction(section=section,
                                                                                  market_ticker=next_ticker,
                                                                                  limit_ticker=perp_ticker,
                                                                                  total_amount=round(
                                                                                      (1 - coef) * close_amount)))
        return update_instructions
