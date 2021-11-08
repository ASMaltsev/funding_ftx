from strategy.others import inverse_operation


class GeneratePosition:

    def __init__(self):
        _open_position = {
            'limit_side': 'buy',
            'market_side': 'sell',
            'reduce_only': False,
        }
        _close_position = {
            'limit_side': inverse_operation(_open_position['limit_side']),
            'market_side': inverse_operation(_open_position['market_side']),
            'reduce_only': not _open_position['reduce_only'],
        }

        self.open_position = {
            'market_ticker': '',
            'limit_ticker': '',
            'total_amount': 0,
            'section': '',
        }
        self.open_position.update(_open_position)

        self.close_position = {
            'market_ticker': '',
            'limit_ticker': '',
            'total_amount': 0,
            'section': '',
        }
        self.close_position.update(_close_position)

    def get_open_position_instruction(self, section, market_ticker, limit_ticker, total_amount):
        self.open_position['section'] = section
        self.open_position['market_ticker'] = market_ticker
        self.open_position['limit_ticker'] = limit_ticker
        self.open_position['total_amount'] = total_amount
        return self.open_position.copy()

    def get_close_position_instruction(self, section, market_ticker, limit_ticker, total_amount):
        self.close_position['section'] = section
        self.close_position['market_ticker'] = market_ticker
        self.close_position['limit_ticker'] = limit_ticker
        self.close_position['total_amount'] = total_amount
        return self.close_position.copy()
