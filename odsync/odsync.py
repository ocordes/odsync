#!/usr/bin/env python

"""
odsync/odsync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver Cordes 2020-11-23
"""


import logging

import sys
import getopt


from sync_logger import init_logger


from command import Daemon, Client


short_options = 'hbtv'
long_options = ['help', 'daemon', 'speed-test', 'verbose', 'host=']


def usage():
    print('Usage:')
    print(' -v|--verbose : verbose output')

def main():
    command = 'copy'

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    verbose = False
    host    = None

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
        elif o in ('--host'):
            host = a
        elif o in ('-t', '--speed-test'):
            command = 'test'
        else:
            assert False, "unhandled option"

    # setup the main logging facility
    init_logger()

    # open an app logger channel
    app_logger = logging.getLogger('App')
    app_logger.debug('App started')

    # do something
    print('args:', args)

    # initialize the client
    client = Client(verbose=verbose, host=host)

    # check if protocol is compatible
    compatible = client.check_protocol()

    if compatible:
        print('Transfer protocol is compatible!')

    # do something useful
    if command == 'copy':
        print('Copy mode')
    elif command == 'test':
        print('Testing mode')
        client.test_speed()

    # Quit the session
    client.send_command(b'QQ')
    client.read_output()

    client.statistic()
    app_logger.debug('App finished')


# main

if __name__ == "__main__":
    main()
