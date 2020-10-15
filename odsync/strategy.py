"""

odsync/strategy.py

written by: Oliver Cordes 2020-10-16
changed by: Oliver Cordes 2020-10-16

"""


def bestblocksize(file1, file2):
    blocksize = file1.get_blocksize()
    blocksize = file2.set_blocksize(blocksize)
    blocksize = file1.set_blocksize(blocksize)

    return blocksize


def copyfile(file1, file2):

    print(f'Copying file: {file1.filename()} -> {file2.filename()}')

    print(file1.open())
    print(file2.open())

    blocksize = bestblocksize(file1, file2)
    print(f'{file1.filename()}: {file1.get_filesize()} bytes')
    print(f'{file2.filename()}: {file2.get_filesize()} bytes')
    print(f'best blocksize: {blocksize} bytes')


    max_size = file1.get_filesize()
    file_pos = 0

    abort = False
    while (file_pos < max_size) and (abort == False):
        abort = True

    file1.close()
    file2.close()

    print('Done.')
