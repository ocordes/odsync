#!/usr/bin/env python

import sys, os
import fcntl
import time
import select



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
    rlist = [sys.stdin.buffer]
    count = 0
    poll = select.poll()

    stdin = os.dup(0)
    stdin = sys.stdin.buffer

    poll.register(stdin, select.POLLIN | select.POLLHUP | select.POLLPRI)
    print(select.POLLIN, file=sys.stderr)
    print(select.POLLPRI, file=sys.stderr)
    print(select.POLLHUP, file=sys.stderr)
    print(select.POLLOUT, file=sys.stderr)
    print(select.POLLERR, file=sys.stderr)
    #print(select.POLLRDHUP, file=sys.stderr)
    print(select.POLLNVAL, file=sys.stderr)
    while running:
        res = poll.poll(5*1000)
        print(res, file=sys.stderr)

        if res:
            res = res[0][1]


            if (res & select.POLLIN) == select.POLLIN:
                new_data = sys.stdin.buffer.read(block_size)

                if len(new_data) > 0:
                #print(len(new_data), file=sys.stderr)
                    recv_bytes += len(new_data)
                #data += new_data
                    print('.', end='', file=sys.stderr)
                    if len(data) > 2*block_size:
                        data = []
            if (res & select.POLLHUP) == select.POLLHUP:
                print(file=sys.stderr)
                print('Pipe is closed!', file=sys.stderr)
                running = False
        else:
            print('Timeout', file=sys.stderr)
            running = False
    end_time = time.time()
    rel_time = end_time - start_time

    print(file=sys.stderr)
    print(f'{recv_bytes} bytes read', file=sys.stderr)

    print(f'transfer rate: {recv_bytes/(rel_time*1024*1024)} MB/s', file=sys.stderr)

    print('Done.', file=sys.stderr)
