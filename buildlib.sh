#!/bin/bash
mkdir build
gcc -I/usr/include/python2.7 -fPIC -shared -o build/libsphaira.so src/lib/sphaira.c
