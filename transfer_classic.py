#!/usr/bin/env python

import sys, os
import fcntl
import time



def setNonBlocking(fd):
    """
    Set the file description of the given file descriptor to non-blocking.
    """
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


# __main__

block_size = 65536


if __name__ == '__main__':
    print('Reading ...', file=sys.stderr)

    #setNonBlocking(sys.stdin)

    running = True
    recv_bytes = 0
    start_time = time.time()
    data = []
    while running:
        new_data = sys.stdin.buffer.read(block_size)
        if new_data:
            recv_bytes += len(new_data)
            #data += new_data
            print('.', end='', file=sys.stderr)
            if len(data) > 2*block_size:
                data = []
        else:
            running = False
            print(len(data), file=sys.stderr)
    end_time = time.time()
    rel_time = end_time - start_time

    print(file=sys.stderr)
    print(f'{recv_bytes} bytes read', file=sys.stderr)

    print(f'transfer rate: {recv_bytes/(rel_time*1024*1024)} MB/s', file=sys.stderr)

    print('Done.', file=sys.stderr)
