import telebot
import signal
import logging
from datetime import datetime
from strategy.others import CLIENT_NAME, HOSTS
from elasticsearch import Elasticsearch

file_path = f'{CLIENT_NAME}_{datetime.utcnow().replace(microsecond=0, second=0)}.log'
flag = False

es = Elasticsearch(HOSTS)


def send_log():
    if not flag:
        bot = telebot.TeleBot(
            token='2082278568:AAF1NVUcgmS1x5X4hFvkzxc6YsoePbmy0Vk')
        chat_id = '368392600'
        f = open(file_path, 'rb')
        bot.send_document(chat_id, f)


def signal_handler(signum, frame):
    global flag
    send_log()
    flag = True
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


class CustomAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        dict_kwargs = kwargs.get('extra', '')
        max_rpc = 0
        current_rpc = 0
        delta = 0
        market_amount = 0
        limit_amount = 0
        line_kwargs = ''
        if dict_kwargs != '':
            line_kwargs = ', '.join(map(str, [f'{k} = {v}' for k, v in dict_kwargs.items()]))
        line = '%s %s' % (msg, line_kwargs)

        if msg == 'Rate limits:':
            current_rpc = dict_kwargs['current_rpc']
            max_rpc = dict_kwargs['max_rpc']
        elif msg == 'CHECK POSITION.':
            delta = dict_kwargs['delta']
        elif msg == 'Current positions with correction on initial positions:':
            limit_amount = dict_kwargs['limit_amount']
            market_amount = dict_kwargs['market_amount']
        elif msg == 'Current positions:':
            limit_amount = dict_kwargs['limit_amount']
            market_amount = dict_kwargs['market_amount']
            delta = dict_kwargs['delta']

        """
          sending logs to grafana
        """
        robot = 'EXECUTOR'  # problems

        if msg is None:
            msg = 'empty'
        if msg == '':
            msg = 'empty'
        doc = {
            'timestamp': datetime.utcnow(),
            'robot': robot,
            'Msg': str(msg),
            'body': line_kwargs,
            'limit_amount': limit_amount,
            'market_amount': market_amount,
            'delta': delta,
            'current_rpc': current_rpc,
            'max_rpc': max_rpc,
            'label': CLIENT_NAME,
        }
        # CLIENT_NAME - name container

        # elastic DB settings
        index_name = 'funding_prod'
        d_type = 'LOGS'

        # es.index(index=index_name, doc_type=d_type, body=doc)
        return line, kwargs


class Logger:
    def __init__(self, name):
        self.name = name

    def create(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        handler_stream = logging.StreamHandler()
        handler_file = logging.FileHandler(file_path)
        handler_file.setLevel(logging.INFO)

        strfmt = '%(asctime)s.%(msecs)06d  %(levelname)s [%(name)s]  %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'

        formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

        handler_file.setFormatter(formatter)
        handler_stream.setFormatter(formatter)

        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)
        adapter = CustomAdapter(logger, None)
        return adapter
