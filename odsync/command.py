"""

odsync/command.py

written by: Oliver Cordes 2020-11-15
changed by: Oliver Cordes 2020-11-23

"""

import sys, os, fcntl, select
import subprocess
import time
import logging

try:
    import numpy as np
    block_testing = True
except:
    print('Block testing disbabled!')
    block_testing = False




remote_exec = 'odsync -b'


block_size = 66536
#block_size = 8192

protocol = '0.0.1'

# helper functions

def setNonBlocking(fd):
    """
    Set the file description of the given file descriptor to non-blocking.
    """
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)



def split_command(data):
    cmd = data[:2]
    s = data[2:].split(b'\0')
    blen = int(s[0])
    bdata = s[1]

    cmd_len = 2+len(s[0])+1+blen

    return cmd, blen, bdata, cmd_len


def bytes2human(size):
    if size < 1000:
        return f'{size} bytes'
    size /= 1024
    if size < 1000:
        return f'{size:.2f} kbytes'
    size /= 1024
    if size < 1000:
        return f'{size:.2f} Mbytes'
    size /= 1024
    return f'{size:.2f} GBytes'



class Daemon(object):
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._running = True

        # set sys.stdin non-blocking
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

        self._poll = select.poll()
        self._poll.register(sys.stdin, select.POLLIN | select.POLLHUP )


    def read_datablock(self, data):
        pass


        # send_data
    #
    # sends a data block to the client, the format is:
    # command (2chars) blocklen (ascii number) \0 [data]
    def send_data(self, cmd, data=None):
        sys.stdout.buffer.write(cmd)
        if data:
            block_len = len(data)
        else:
            block_len = 0
        block_len = str(block_len).encode('ascii')

        sys.stdout.buffer.write(block_len)
        sys.stdout.buffer.write(b'\0')
        if data:
            sys.stdout.buffer.write(data)
        sys.stdout.flush()


    def process_event(self, data):
        if data:
            cmd, blen, bdata, cmd_len = split_command(data)
            #print(f' cmd:     {cmd}', file=sys.stderr)
            #print(f' len:     {blen}', file=sys.stderr)
            #print(f' cmd_len: {cmd_len}', file=sys.stderr)

            # if cmd structure does not fit into the data,
            # which means that data is still to be read,
            # then postpone the handling!
            if cmd_len > len(data):
                #print(f'>>{len(data)} buffer was not complete', file=sys.stderr)
                return data

            # handle events
            if cmd == b'QQ':
                # QUIT
                self._running = False
            elif cmd == b'VV':
                # Version request
                prot = f'ODS-{protocol}'.encode('ascii')
                #print(f' send: {prot}', file=sys.stderr)
                #time.sleep(1)
                self.send_data(b'SS', data=prot)
            elif cmd == b'BW':
                self.send_data(b'SS', data=b'OK')
                #pass
            data = data[cmd_len:]
            #print(f' rest:    {len(data)}', file=sys.stderr)
        return data


    def handle_events(self):
        print('handle_events', file=sys.stderr)

        data = b''
        # need a strategy of reading and handling of streams!!!

        timeout = 1000
        while self._running:
            res = self._poll.poll(timeout)
            #print(res)

            if res:
                flags = res[0][1]
                #print(flags)

                if (flags & select.POLLIN) == select.POLLIN:
                    # data are available

                    newdata = sys.stdin.buffer.read(block_size*2)

                    if newdata:
                        #if len(data) > 0:
                        #    print(f'>>{len(data)} buffer was not empty', file=sys.stderr)
                        data += newdata

                    if data:
                        #print(f'>>{data[:6]}', file=sys.stderr)
                        data = self.process_event(data)

        print('QUIT')



class Client(object):
    def __init__(self, host=None, verbose=False):
        self._verbose = verbose
        self._protocol = protocol

        self._send_bytes = 0
        self._recv_bytes = 0

        self._logger = logging.getLogger(self.__class__.__name__)

        if host:
            cmd = f'ssh {host} {remote_exec}'
        else:
            cmd = f'{remote_exec}'
        self._pipe = subprocess.Popen(cmd, shell=True,# bufsize=1,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)


        self._poll = select.poll()
        self._poll.register(self._pipe.stdout, select.POLLIN | select.POLLHUP )

        setNonBlocking(self._pipe.stdout)
        #setNonBlocking(self._pipe.stderr.fileno())


    # send_command
    #
    # sends a command to the daemon, the format is:
    # command (2chars) blocklen (ascii number) \0 [data]
    def send_command(self, cmd, data=None):
        self._pipe.stdin.write(cmd)
        if data:
            block_len = len(data)
            size = block_len
        else:
            block_len = 0
            size = 0
        block_len = str(block_len).encode('ascii')
        self._pipe.stdin.write(block_len)
        self._pipe.stdin.write(b'\0')
        if data:
            self._pipe.stdin.write(data)
        self._pipe.stdin.flush()

        self._send_bytes += 3+len(block_len)+size


    # read_output
    #
    # reads the result from the daemon
    def read_output(self, timeout=None):
        have_no_data = True
        wait_time = 0.0
        data = None
        if timeout is None:
            timeout = 1

        # timeout must be given in milliseconds
        timeout *= 1000
        while have_no_data:
            res = self._poll.poll(timeout)
            #print(res)

            if res:
                flags = res[0][1]
                #print(flags)

                if (flags & select.POLLIN) == select.POLLIN:
                    # data are available

                    data = self._pipe.stdout.read(block_size*2)
                    #data = self._pipe.stdout.read()
                    if data:
                        self._logger.debug(f'{len(data)} bytes recieved')
                        self._recv_bytes += len(data)
                        #print('R', data)
                        have_no_data = False
            else:
                print('Timeout!')
                return None
        return data


    # check_protocol
    #
    # checks if both version of the protocol is compatible
    # save the minimum version in self._protocol for tests
    def check_protocol(self):
        self.send_command(b'VV')

        data = self.read_output(timeout=30)
        cmd, blen, bdata, cmd_len = split_command(data)
        print(f' cmd:     {cmd}')
        print(f' len:     {blen}')
        print(f' cmd_len: {cmd_len}')
        print(f' data:    {bdata}')

        protocol_recv = bdata.decode('utf-8')

        version = protocol_recv.split('-')[1]
        self._protocol = min(version, protocol)
        return (version >= protocol)


    def speed_write_block(self, length, times):
        start_time = time.time()
        for _ in range(times):
            data = np.random.bytes(length)
            self.send_command(b'BW', data=data)

            data = self.read_output()
            cmd, blen, bdata, cmd_len = split_command(data)
        end_time = time.time()

        return end_time - start_time


    def test_speed(self):
        if block_testing == False:
            print('Tests cannot be performed! Please install numpy library!')
            return

        print('Perform speed tests ...')

        length = block_size
        times = 1000

        run_time = self.speed_write_block(length, times)

        print(f' {length*times/(1024*1024)} MB in {run_time} seconds')
        print(f' transfer rate: {length*times/(run_time*1024*1024):.2f}MB/s')
        #data = np.random.bytes(512)
        #self.send_command(b'BW', data=data)
        #self.write_block(data)

        print('Done.')


    def statistic(self):
        print('Transfer statistics:')
        print(f' {bytes2human(self._send_bytes)} transferred')
        print(f' {bytes2human(self._recv_bytes)} recieved')
