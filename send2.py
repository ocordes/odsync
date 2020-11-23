#!/usr/bin/env python

import sys, os

import subprocess


block_size = 65535




# __main__

if __name__ == '__main__':

    cmd = './transfer.py'
    pipe = subprocess.Popen(cmd, shell=True,# bufsize=1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE)

    print('Writing...', file=sys.stderr)
    with open(sys.argv[1], 'rb') as f:
        running = True

        bytes_read = 0
        while running:
            data = f.read(block_size)
            if data:
                bytes_read += len(data)
                #sys.stdout.buffer.write(data)
                #sys.stdout.flush()
                for _ in range(5):
                    pipe.stdin.write(data)
                    pipe.stdin.flush()
            else:
                running = False

    print(f'{bytes_read} bytes read from file', file=sys.stderr)

    print('Done writing.', file=sys.stderr)
