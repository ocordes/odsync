#!/usr/bin/env python

"""
odsync/odsync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver COrdes 2020-11-08
"""


import logging


from sync_strategy import copyfile, \
        strategy_simple, strategy_md5sum, strategy_opt1
from sync import SyncLocalFile
from sync_logger import init_logger


# main

# setup the main logging facility
init_logger()

# open an app logger channel
app_logger = logging.getLogger('App')
app_logger.debug('App started')



file1 = SyncLocalFile('test1.dat')
file2 = SyncLocalFile('test2.dat', write=True)

copy_strategy = strategy_md5sum
copyfile(file1, file2, copy_strategy=copy_strategy)

app_logger.debug('App finished')
