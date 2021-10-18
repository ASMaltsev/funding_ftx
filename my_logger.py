import coloredlogs
import logging


class Logger:

    def create(self, logger_name):
        logging.basicConfig(filename=f'{logger_name}.log', filemode='w')
        my_logs = logging.getLogger(logger_name)

        fieldstyle = {'asctime': {'color': 'green'},
                      'levelname': {'bold': False, 'color': 'green'},
                      'filename': {'color': 'cyan'},
                      'funcName': {'color': 'blue'}}

        levelstyles = {'critical': {'bold': True, 'color': 'red'},
                       'debug': {'color': 'green'},
                       'error': {'color': 'red'},
                       'info': {'color': 'magenta'},
                       'warning': {'color': 'yellow'}}

        coloredlogs.install(level=logging.DEBUG,
                            logger=my_logs,
                            fmt='%(asctime)s.%(msecs)d06 %(levelname)s: %(message)s',
                            datefmt='%H:%M:%S',
                            field_styles=fieldstyle,
                            level_styles=levelstyles, syslog=True)
