#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    Chel.py
@author  PERROCHAUD Clément
@version 0.1
@date    2013-10-28

Programme principal du superviseur.
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import subprocess as sp
import mmap
import time
import os
import stat
# DEBUG
from random import randint

# CONSTANTES ###################################################################

VALUES_FILE = "/tmp/values.chel"

# MAIN #########################################################################

if __name__ == "__main__":
    print("Populating value file...")
    vf = open(VALUES_FILE, "wb")
    for i in range(2047):
        vf.write(38*b"#"+b"\n")
    vf.flush()
    vf.close()

    os.chmod(VALUES_FILE, 2047)

    print("Opening value file...")
    vf = open(VALUES_FILE, "r+b")
    vf.flush()

    print("Mapping value file...")
    mmvf = mmap.mmap(vf.fileno(), 0, access=mmap.ACCESS_WRITE)

    print("Writing random stuff ad nauseum...")
    while 1:
        mmvf.seek(0)
        for i in range(4):
            mmvf.write("{0}\t{1}\t{2:2.4g}\t{3:3.5g}\t{4:4.6g}\t{5:2.4g}\t{6:3.5g}\n".format(i,
                randint(1,4),
                randint(900, 1800)/100,
                randint(0, 16400)/100,
                randint(0, 300000)/100,
                randint(0, 3600)/100,
                randint(0, 16400)/100).encode("utf-8"))
        mmvf.write(b"#\n")
        time.sleep(0.5)

    print("Closing value file...")
    mmvf.close()
    vf.close()
