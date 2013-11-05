#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    ABBServer.py
@author  PERROCHAUD Clément
@version 1.3
@date    2013-11-02

Serveur répondant aux requêtes de l'interface Android/PC.
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import socket
import mmap
import re
import sys

# CONSTANTES ###################################################################

VALUES_FILE = "/tmp/values.chel"

HOST = ""

PORT = 1234

REQU_REGEX = re.compile(r"([0-9]{1,3})\t(00?|18|24|30|36)\n")

# MAIN #########################################################################

if __name__ == "__main__":

    # Ouverture du fichier valeurs
    vf = open(VALUES_FILE, "rb")
    mmvf = mmap.mmap(vf.fileno(), 0, access=mmap.ACCESS_READ)

    # Ouverture du socket d'écoute
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    # Attente de l'ouverture de la liaison par le client Chak
    conn, addr = s.accept()

    while True:

        # Réception de la consigne
        try:
            request = conn.recv(8).decode("utf-8")
        except ConnectionResetError:
            request = ""
        except UnicodeDecodeError:
            continue

        # Déconnexion, attente d'un nouveau client
        if not request:
            conn, addr = s.accept()
            continue

        # Vérification du format de la requête
        m = re.match(REQU_REGEX, request)
        if not m:
            continue

        # Correction du format de la requête
        request = "{0:03}\t{1:02}\n".format(int(m.group(1)), int(m.group(2)))

        # Transmission de la consigne à PBBMaster
        if request[4:6] != "00":
            sys.stdout.write(request)
            sys.stdout.flush()

        # Assemblage de la réponse
        answer = b""
        mmvf.seek(0)
        while True:
            line = mmvf.readline()
            if not line:
                break
            elif line[0:1] == b"#":
                continue
            answer += line[:-1]+b":"
        answer += b"\n"

        # Réponse
        conn.sendall(answer)

    # Fermeture du fichier valeurs
    mmvf.close()
    vf.close()
