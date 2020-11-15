"""

odsync/command.py

written by: Oliver Cordes 2020-11-15
changed by: Oliver Cordes 2020-11-15

"""

import sys, os, fcntl
import subprocess
import time


remote_exec = '/Users/ocordes/git/odsync/odsync.sh'

block_size = 4096

protocol = 'ODS-0.0.1'

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

        # set sys.stdin non-blocking
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)


    def handle_events(self):
        print('handle_events', file=sys.stderr)
        running = True

        while running:
            data = sys.stdin.read(block_size)
            #data = sys.stdin.read()
            if data:
                print(f'>>{data}', file=sys.stderr)
                #print(data)
                if data[0] == 'Q':
                    running = False
                elif data[0] == 'V':
                    #time.sleep(30)
                    sys.stdout.write(protocol)
                    sys.stdout.flush()
                    #print(protocol, flush=True)

                    #running = False
            #running = False

        print('QUIT')



class Client(object):
    def __init__(self, verbose=False):
        self._verbose = verbose

        cmd = f'{remote_exec} -b'
        self._pipe = subprocess.Popen(cmd, shell=True,# bufsize=1,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)


        setNonBlocking(self._pipe.stdout)
        #setNonBlocking(self._pipe.stderr.fileno())


    def send_command(self, cmd):
        #print(dir(self._pipe.stdout))
        self._pipe.stdin.write(cmd)
        self._pipe.stdin.flush()


    def read_output(self, timeout=None):
        have_no_data = True
        wait_time = 0.0
        data = None
        while have_no_data:
            data = self._pipe.stdout.read()
            if data:
                print('2', data)
                have_no_data = False
            else:
                time.sleep(0.01)
                wait_time += 0.01
                if timeout is not None:
                    if wait_time > timeout:
                        print('Timeout!')
                        return None
        return data
        #print('2', self._pipe.stdout.readlines())


    def check_protocol(self):
        self.send_command(b'V')
        protocol_recv = self.read_output().decode('utf-8')

        print(protocol_recv)

        
