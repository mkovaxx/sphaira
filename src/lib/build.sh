#!/bin/bash
gcc -I/usr/include/python2.7 -fPIC -shared -o libsphaira.so sphaira.c
