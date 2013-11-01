#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    PBBMaster.py
@author  PERROCHAUD Clément
@version 0.1
@date    2013-10-29

Superviseur du bus CAN
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import struct
import time
import socket
#DEBUG
from random import randint, choice

FRAME_FORMAT = b"=IB3x8s"
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)

def buildFame(num, data, requ=False):
    arbitration = num << 3
    if requ:
        arbitration += 2
    dlc = len(data)
    data = data.ljust(8, b'\x00')
    return struct.pack(FRAME_FORMAT, arbitration, dlc, data)

def dissectFrame(frame):
    num, dlc, data = struct.unpack(FRAME_FORMAT, frame)
    return (num, data[:dlc])

if __name__=="__main__":

    canSocket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    canSocket.bind(('can0',))

    while 1:

        canSocket.send(buildFrame(0x01, b"Salut", False))

        cf, addr = canSocket.recvfrom(FRAME_SIZE)

        print("{}: {}".format(*dissectFrame(cf)))

    #    for i in range(4):
    #        print("{}\t{}\t{}\t{}\t{}\n".format(i
    #                                            choice((0, 63, 127, 255)),
    #                                            randint(0, 255),
    #                                            randint(0, 255),
    #                                            randint(0, 255)))

        time.sleep(0.5)
