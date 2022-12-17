#!/bin/bash
make
./mkfs -f test.img
base=$(dirname "$0")
killall server
pkill -9 -u $USER -f "/home/cs537-1/tests/p4/Python-2.7.1/python  $base/project4.py"
/home/cs537-1/tests/p4/Python-2.7.1/python $base/project4.py --test-path $base $@ | tee -i runtests.log
exit $?
