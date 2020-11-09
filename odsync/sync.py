"""
odsync/sync.py

written by: Oliver Cordes 2020-10-15
changed by: Oliver Cordes 2020-11-08

"""

import io
import os
import hashlib

import sync_strategy

from sync_exceptions import SyncException

import logging



class SyncFile(object):
    def __init__(self):
        self._blocksize = -1
        self._filesize = 0

        self._bytes_written = 0
        self._bytes_read = 0
        self._bytes_transferred = 0
        self._bytes_info = 0

        # add a syncfile logger
        self._logger = logging.getLogger(self.__class__.__name__)


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


    def write_block(self, data):
        raise NotImplementedError


    def read_block(self):
        raise NotImplementedError


    def clear_data(self):
        raise NotImplementedError


    def read_data(self):
        raise NotImplementedError


    def read_md5_signature(self):
        raise NotImplementedError


    def copy_to_simple(self, tofile):
        data = self.read_block()
        tofile.write_block(data)

        return self._blocksize


    def copy_to_md5sum(self, tofile):
        must_write = False

        read_len = self.read_data()
        write_len = tofile.read_data()
        print(f'read len:  {read_len}')
        print(f'write len: {write_len}')

        if read_len != write_len:
            must_write = True
        else:
            read_md5_signature = self.read_md5_signature()
            write_md5sum_signature = tofile.read_md5_signature()
            print(f'read:  {read_md5_signature}')
            print(f'write: {write_md5sum_signature}')
            if read_md5_signature != write_md5sum_signature:
                must_write = True

        print(f'must_write = {must_write}')

        self.clear_data()
        tofile.clear_data()

        return self._blocksize


    def copy_to_opt1(self, tofile):
        return self._blocksize


    def copy_to(self, tofile, strategy=sync_strategy.strategy_simple):
        if strategy == sync_strategy.strategy_simple:
            bytes = self.copy_to_simple(tofile)
        elif strategy == sync_strategy.strategy_md5sum:
            bytes = self.copy_to_md5sum(tofile)
        elif strategy == sync_strategy.strategy.opt1:
            bytes = self.copy_to_opt1(tofile)
        else:
            bytes = self._blocksize

        return bytes



class SyncLocalFile(SyncFile):
    def __init__(self, filename, write=False):
        SyncFile.__init__(self)
        self._filename  = filename
        self._write     = write
        self._blocksize = io.DEFAULT_BUFFER_SIZE
        self._data      = None


    def filename(self):
        return self._filename


    def read_block(self):
        data = self._fd.read(self._blocksize)
        self._bytes_read += len(data)
        self._logger.debug(f'read {len(data)} bytes')
        return data


    def write_block(self, data):
        try:
            b = self._fd.write(data)
        except IOerror as e:
            raise SyncException(f'IOError {e}')
        self._bytes_written += b
        self._logger.debug(f'write {b} bytes')

    def open(self):
        if self._write:
            if (os.access(self._filename, os.R_OK or os._W_OK)):
                mode = 'r+b'
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
            return False, f'Can\'t open file {self._filename}'


    def clear_data(self):
        self._data = None


    def read_data(self):
        self._data = self.read_block()

        return len(self._data)


    def read_md5_signature(self):
        if self._data is not None:
            md5 = hashlib.md5()
            md5.update(self._data)
            return md5.hexdigest()
        else:
            return None
