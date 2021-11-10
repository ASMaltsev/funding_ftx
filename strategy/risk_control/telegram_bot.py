import telebot
import ast
import time
from telebot import types

# #INS
# token = '2141088886:AAGhy42cmvbvgGmSfJ_3wxd00lL3MYjZ3HA'
# chat_id = -711071654


#TEST API
token = '2116226519:AAEPqDgHtE6Rs-fTVttpeM7rwH3IiIWnb-Y'
chat_id = -766294450

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['ok'])
def action(call):
    if call.chat.id == chat_id:
        bot.stop_bot()


class TelegramBot:

    """
    @return: True if OK False otherwise
    """

    def __init__(self, chat_id):
        self.bot = bot
        self.chat_id = chat_id


    def start(self, final_instructions, real_positions) -> bool:
        self.bot.send_message(chat_id=self.chat_id, text=real_positions)
        self.bot.send_message(chat_id=self.chat_id, text=final_instructions)

        self.bot.polling(none_stop=True, interval=0, timeout=20)
