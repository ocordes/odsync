"""
odsync/sync_logger.py

written by: Oliver Cordes 2020-10-25
changed by: Oliver Cordes 2020-10-25

"""


import logging
import logging.handlers

LOG_FILENAME = 'odsync.log'


def init_logger(logfile=LOG_FILENAME):
    # create the root logger

    handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=65536, backupCount=5)
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-14s %(levelname)s %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S',
                    #filename=LOG_FILENAME,
                    handlers=[handler] )
                    #filemode='w')
