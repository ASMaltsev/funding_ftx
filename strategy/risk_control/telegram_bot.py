import telebot
import time


# #INS
# token = '2141088886:AAGhy42cmvbvgGmSfJ_3wxd00lL3MYjZ3HA'
# chat_id = -711071654


class TelegramBot:

    def __init__(self):
        self.token = '2098325312:AAFrwnuX1JeBBd1i8KjXUyXCvYgw8g-3__I'
        self.chat_id = -725423248
        self.bot = telebot.TeleBot(self.token, threaded=False)
        self.flag = False

    def start(self, final_instructions, real_positions):

        self.bot.send_message(chat_id=self.chat_id, text=f'Real_position = {real_positions}')
        self.bot.send_message(chat_id=self.chat_id, text=f'Final_instructions = {final_instructions}')

        @self.bot.message_handler(content_types=['text'])
        def go(message):
            if message.text == 'ok' and message.date > time.time() - 2:
                self.flag = True
                self.bot.stop_polling()
            if message.text == 'stop' and message.date > time.time() - 2:
                self.flag = False
                self.bot.stop_polling()

        self.bot.infinity_polling()
        return self.flag

    def send_message(self, msg):
        self.bot.send_message(chat_id=self.chat_id, text=msg)
