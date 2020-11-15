#!/usr/bin/env python

"""
odsync/odsync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver COrdes 2020-11-15
"""


import logging

import sys
import getopt


from sync_logger import init_logger


from command import Daemon, Client


short_options = 'hbv'
long_options = ['help', 'daemon', 'verbose']


def usage():
    print('Usage:')
    print(' -v|--verbose : verbose output')

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    verbose = False
    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-b', '--daemon'):
            # don't write something to stdout, because it is piped ;-)
            daemon = Daemon(verbose=verbose)
            daemon.handle_events()
            sys.exit()
        else:
            assert False, "unhandled option"

    # setup the main logging facility
    init_logger()

    # open an app logger channel
    app_logger = logging.getLogger('App')
    app_logger.debug('App started')

    # do something
    print('Hallo')
    print(args)

    client = Client(verbose=verbose)
    client.check_protocol()
    client.send_command(b'Q')
    client.read_output()

    app_logger.debug('App finished')


# main

if __name__ == "__main__":
    main()
