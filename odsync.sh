#!/bin/bash

DIR=$(dirname $0)

(cd $DIR; python3 odsync/odsync.py $*)
