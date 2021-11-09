import telebot
import ast
import time
from telebot import types

token = '2116226519:AAEPqDgHtE6Rs-fTVttpeM7rwH3IiIWnb-Y'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['ok'])
def action():
    self.bot.stop_bot()

class TelegramBot:

    """
    @return: True if OK False otherwise
    """

    def __init__(self):
        self.bot = bot
        self.chat_id = -766294450


    def start(self, final_instructions, real_positions) -> bool:
        self.bot.send_message(chat_id=self.chat_id, text=real_positions)
        self.bot.send_message(chat_id=self.chat_id, text=final_instructions)

        try:
            self.bot.polling(none_stop=False, interval=0, timeout=20)
        except:
            return True
