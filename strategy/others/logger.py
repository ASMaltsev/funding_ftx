import logging
from datetime import datetime
from constants import client_name


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
        handler_file = logging.FileHandler(
            f'{client_name}_{datetime.utcnow().replace(microsecond=0, second=0)}.log')
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
