#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    ABBServer.py
@author  PERROCHAUD Clément
@version 0.1
@date    2013-10-28

Serveur répondant aux requêtes de l'interface Android/PC.
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import socket
import mmap

# CONSTANTES ###################################################################

VALUES_FILE = "/tmp/values.chel"

HOST = ""

PORT = 1234

# MAIN #########################################################################

if __name__ == "__main__":
    vf = open(VALUES_FILE, "rb")
    mmvf = mmap.mmap(vf.fileno(), 0, access=mmap.ACCESS_READ)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    while 1:
        request = conn.recv(8)
        print(request.decode("utf-8"))
        answer = b""
        mmvf.seek(0)
        while 1:
            line = mmvf.readline()
            if line[0] in (35, 10):
                break
            answer += line
        conn.sendall(answer)
    mmvf.close()
    vf.close()
