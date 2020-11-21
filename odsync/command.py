"""

odsync/command.py

written by: Oliver Cordes 2020-11-15
changed by: Oliver Cordes 2020-11-21

"""

import sys, os, fcntl
import subprocess
import time
import logging

try:
    import numpy as np
    block_testing = True
except:
    print('Block testing disbabled!')
    block_testing = False



remote_exec = '/Users/ocordes/git/odsync/odsync.sh'

block_size = 4096

protocol = '0.0.1'

# helper functions

def setNonBlocking(fd):
    """
    Set the file description of the given file descriptor to non-blocking.
    """
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)



class Daemon(object):
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._running = True

        # set sys.stdin non-blocking
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)


    def read_datablock(self, data):
        pass


    def process_event(self, data):
        if data:
            if data[0] == 'Q':
                self._running = False
                data = []
            elif data[0] == 'V':
                sys.stdout.write('ODS-'+protocol)
                sys.stdout.flush()
                data = data[1:]

        return data

    def handle_events(self):
        print('handle_events', file=sys.stderr)

        # need a strategy of reading and handling of streams!!!
        while self._running:
            data = sys.stdin.read(block_size)
            #data = sys.stdin.read()
            if data:
                print(f'>>{data}', file=sys.stderr)
                #print(data)
                data = self.process_event(data)

        print('QUIT')



class Client(object):
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._protocol = protocol

        self._logger = logging.getLogger(self.__class__.__name__)

        cmd = f'{remote_exec} -b'
        self._pipe = subprocess.Popen(cmd, shell=True,# bufsize=1,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)


        setNonBlocking(self._pipe.stdout)
        #setNonBlocking(self._pipe.stderr.fileno())


    # send_command
    #
    # sends a command to the daemon
    def send_command(self, cmd):
        self._pipe.stdin.write(cmd)
        self._pipe.stdin.flush()

    # read_output
    #
    # reads the result from the daemon
    def read_output(self, timeout=None):
        have_no_data = True
        wait_time = 0.0
        data = None
        while have_no_data:
            data = self._pipe.stdout.read()
            if data:
                self._logger.debug(f'{len(data)} bytes recieved')
                print('R', data)
                have_no_data = False
            else:
                time.sleep(0.01)
                wait_time += 0.01
                if timeout is not None:
                    if wait_time > timeout:
                        print('Timeout!')
                        return None
        return data


    # check_protocol
    #
    # checks if both version of the protocol is compatible
    # save the minimum version in self._protocol for tests
    def check_protocol(self):
        self.send_command(b'V')
        protocol_recv = self.read_output().decode('utf-8')

        version = protocol_recv.split('-')[1]
        self._protocol = min(version, protocol)
        return (version >= protocol)


    def write_block(self, data):
        block_len = str(len(data)).encode('ascii')
        return

        self._pipe.stdin.write(b'B')
        self._pipe.stdin.write(block_len)
        self._pipe.stdin.write(b'\0')
        self._pipe.stdin.write(b'\n')
        self._pipe.stdin.flush()


    def test_speed(self):
        if block_testing == False:
            print('Tests cannot be performed! Please install numpy library!')
            return

        print('Perform speed tests ...')
        data = np.random.bytes(512)
        self.write_block(data)
        print('Done.')
