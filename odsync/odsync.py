#!/usr/bin/env python

from strategy import copyfile

from sync import SyncLocalFile

# main

file1 = SyncLocalFile('test1.dat')
file2 = SyncLocalFile('test2.dat', write=True)

copyfile(file1,file2)
