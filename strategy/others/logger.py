import telebot

import signal
import logging
from datetime import datetime
from constants import client_name

file_path = ''


def send_log():
    print(file_path)
    if file_path != '':
        bot = telebot.TeleBot(
            token='2082278568:AAF1NVUcgmS1x5X4hFvkzxc6YsoePbmy0Vk')
        chat_id = '368392600'
        f = open(file_path, 'rb')
        bot.send_document(chat_id, f)


# Our signal handler
def signal_handler(signum, frame):
    send_log()
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


class CustomAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        dict_kwargs = kwargs.get('extra', '')
        line_kwargs = ''
        if dict_kwargs != '':
            line_kwargs = ', '.join(map(str, [f'{k} = {v}' for k, v in dict_kwargs.items()]))
        line = '%s %s' % (msg, line_kwargs)

        return line, kwargs


class Logger:
    def __init__(self, name):
        self.name = name

    def create(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        handler_stream = logging.StreamHandler()
        file_path = f'{client_name}_{datetime.utcnow().replace(microsecond=0, second=0)}.log'
        handler_file = logging.FileHandler(file_path)
        handler_file.setLevel(logging.DEBUG)

        strfmt = '%(asctime)s.%(msecs)06d  %(levelname)s [%(name)s]  %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'

        formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

        handler_file.setFormatter(formatter)
        handler_stream.setFormatter(formatter)

        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)
        adapter = CustomAdapter(logger, None)
        return adapter
