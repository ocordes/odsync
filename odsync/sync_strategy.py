"""

odsync/sync_strategy.py

written by: Oliver Cordes 2020-10-16
changed by: Oliver Cordes 2020-11-08

"""

import logging

from sync_exceptions import SyncException

# strategy types
strategy_simple = 0
strategy_md5sum = 1
strategy_opt1   = 2


def bestblocksize(file1, file2):
    blocksize = file1.get_blocksize()
    blocksize = file2.set_blocksize(blocksize)
    blocksize = file1.set_blocksize(blocksize)

    return blocksize


def copyfile(file1, file2, copy_strategy=strategy_simple):

    logger = logging.getLogger('CopyFile')
    print(f'Copying file: {file1.filename()} -> {file2.filename()}')

    print(file1.open())
    print(file2.open())

    blocksize = bestblocksize(file1, file2)
    print(f'{file1.filename()}: {file1.get_filesize()} bytes')
    print(f'{file2.filename()}: {file2.get_filesize()} bytes')
    print(f'best blocksize: {blocksize} bytes')


    max_size = file1.get_filesize()
    file_pos = 0


    if copy_strategy == strategy_simple:
        logger.debug('copying strategy: simple')
    elif copy_strategy == strategy_md5sum:
        logger.debug('copying strategy: md5sum')
    elif copy_strategy == strategy_op1:
        logger.debug('copying strategy: op1')
    else:
        logger.debug('copying strategy: unknown')
        raise SyncException('No valid copying strategy given!')

    try:
        abort = False
        while (file_pos < max_size) and (abort == False):
            file_pos += file1.copy_to(file2, strategy=copy_strategy)
            print(file_pos, end=' ')
            #abort = True

            file1.close()
            file2.close()
    except SyncException as e:
        print()
        print(f'Error during file copying - {e}')


    print('Done.')
