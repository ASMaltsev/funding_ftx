import telebot

bot = telebot.TeleBot(
    token='2082278568:AAF1NVUcgmS1x5X4hFvkzxc6YsoePbmy0Vk')
chat_id = '368392600'
f = open('requirements.txt', 'rb')
bot.send_document(chat_id, f)
