"""
odsync/sync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver Cordes 2020-10-15

"""

import io
import os


class SyncFile(object):
    def __init__(self):
        self._blocksize = -1
        self._filesize = 0


    def open(self):
        return True, 'OK'


    def close(self):
        return True


    def block_info(self):
        raise NotImplementedError


    def block_read(self, data):
        raise NotImplementedError


    def block_write(self, data):
        raise NotImplementedError


    def filename(self):
        raise NotImplementedError


    def get_blocksize(self):
        return self._blocksize


    def get_filesize(self):
        return self._filesize


    def set_blocksize(self, blocksize):
        if blocksize < self._blocksize:
            self._blocksize = blocksize

        return self._blocksize



class SyncLocalFile(SyncFile):
    def __init__(self, filename, write=False):
        SyncFile.__init__(self)
        self._filename = filename
        self._write    = write
        self._blocksize = io.DEFAULT_BUFFER_SIZE


    def filename(self):
        return self._filename


    def open(self):
        if self._write:
            if (os.access(self._filename, os.R_OK or os._W_OK)):
                mode = 'rb+'
            else:
                mode = 'ab'
        else:
            mode = 'rb'
        try:
            self._fd = open(self._filename, mode)

            # check the file_size so far
            # move file cursor to end
            self._fd.seek(0, os.SEEK_END)
            # get the current cursor position
            self._filesize = self._fd.tell()
            self._fd.seek(0, os.SEEK_SET)


            return True, 'OK'
        except:
            return False, 'Can\'t open file'
