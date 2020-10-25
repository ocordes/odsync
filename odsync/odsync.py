#!/usr/bin/env python

"""
odsync/odsync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver COrdes 2020-10-25
"""


import logging


from sync_strategy import copyfile
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

copyfile(file1,file2)

app_logger.debug('App finished')
