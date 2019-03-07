import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from time import sleep

from mysite.settings import BASE_DIR

LEVEL = logging.DEBUG


def getLogger(filename, name=None, level=LEVEL):
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)

    # make sure that the file exists
    if not os.path.exists(filename):
        file_path, file_name = os.path.split(filename)
        os.makedirs(file_path,exist_ok=True)
        # os.mknod(filename,mode=0o777)
        with open(filename, 'a+') as fp:
            pass
    # interval: how many numbers of 'when' will keep the log file
    # backupCount: how many old log files will keep.
    # log_file_handler = TimedRotatingFileHandler(filename=filename, when="D", interval=30, backupCount=3)
    log_file_handler = RotatingFileHandler(filename=filename, maxBytes=50*1024*1024, backupCount=3)

    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s(line %(lineno)d) - %(levelname)s - %(message)s'))
    logger.setLevel(level)
    logger.addHandler(log_file_handler)
    logger.debug('Log file created. File name: %s Logger name: %s'%(filename, name))
    return logger

update_logger = getLogger(os.path.join(BASE_DIR, os.getenv('LOG_DIR','logs'), 'vod.log'), name='vod', level=logging.DEBUG)

