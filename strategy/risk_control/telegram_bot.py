class TelegramBot:

    def __init__(self):
        self.token = ''

    def start(self, final_instructions, real_positions) -> bool:
        """
        @return: True if OK False otherwise
        """