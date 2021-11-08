class GeneratePosition:

    def __init__(self):
        self.market_ticker = ''
        self.limit_ticker = ''
        self.section = ''
        self.total_amount = 0
        self.open_position = {
            'market_ticker': self.market_ticker, 'limit_ticker': self.limit_ticker, 'limit_side': 'buy',
            'market_side': 'sell', 'total_amount': self.total_amount, 'reduce_only': False, 'section': self.section
        }

        self.close_position = {
            'market_ticker': None, 'limit_ticker': None,
            'limit_side': self._inverse_operation(self.open_position['limit_side']),
            'market_side': self._inverse_operation(self.open_position['market_side']), 'total_amount': None,
            'reduce_only': not self.open_position['reduce_only'], 'section': None
        }

    @staticmethod
    def _inverse_operation(operation):
        if operation == 'sell':
            return 'buy'
        elif operation == 'buy':
            return 'sell'

    def generate(self, section, market_ticker, limit_ticker, total_amount):
        self.section = section
        self.market_ticker = market_ticker
        self.limit_ticker = limit_ticker
        self.total_amount = total_amount

    def get_open_position_instruction(self):
        return self.open_position

    def get_close_position_instruction(self):
        return self.close_position
