#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    Chel.py
@author  PERROCHAUD Clément
@version 1.0
@date    2013-11-02

Programme principal du superviseur.
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import subprocess as sp
import mmap
import sys
import os

# CONSTANTES ###################################################################

VALUES_FILE = "/tmp/values.chel"

FORMAT_REPONSE_ABB = ("{0:03}\t"
                      "{1:02}\t"
                      "{2:05.2f}\t"
                      "{3:06.2f}\t"
                      "{4:07.2f}\t"
                      "{5:05.2f}\t"
                      "{6:06.2f}\n")

MAX_BOOSTS = 256

ABBS_FILE = "ABBServer.py"

PBBM_FILE = "PBBMaster"

# MAIN #########################################################################

if __name__ == "__main__":

    scriptDir = os.path.abspath(__file__)

    # Création du fichier valeurs
    print("Populating value file...")
    vf = open(VALUES_FILE, "wb")
    for i in range(MAX_BOOSTS):
        vf.write(40*b"#"+b"\n")
    vf.flush()
    vf.close()

    # Ré-ouverture du fichier valeurs
    print("Opening value file...")
    vf = open(VALUES_FILE, "r+b")
    vf.flush()

    # Mappage du fichier en mémoire
    print("Mapping value file...")
    mmvf = mmap.mmap(vf.fileno(), 0, access=mmap.ACCESS_WRITE)

    # Démarrage de ABBServer
    print("Starting ABBServer...")
    abbProc = sp.Popen([os.join(scriptDir, ABBS_FILE)],
               stdin=sp.PIPE,
               stdout=sp.PIPE,
               stderr=sys.stderr)

    # Démarrage de PBBMaster
    print("Starting PBBMaster...")
    pbbProc = sp.Popen([os.join(scriptDir, PBBM_FILE)],
               stdin=abbProc.stdout,
               stdout=sys.stdin,
               stderr=sys.stderr)

    print("Entering main loop...")
    while True:

        # Lecture des mesures
        try:
            mesures = [ int(x) for x in input().split("\t") ]
        except EOFError:
            break

        # Liste des mesures lues :
        #   mesures[0] = Nboost
        #   mesures[1] = Consigne
        #   mesures[2] = Vi
        #   mesures[3] = Vil
        #   mesures[4] = Vo

        # Navigation dans le fichier valeurs
        mmvf.seek(mesures[0]*41)

        # Calcul des valeurs
        ii = (mesures[3] - mesures[2])/0.055
        pi = mesures[2]*ii
        io = pi/mesures[4]

        # Écriture des valeurs dans le fichier valeurs
        mmvf.write(FORMAT_REPONSE_ABB.format(mesures[0],
                                             mesures[1],
                                             mesures[2],
                                             ii,
                                             pi,
                                             mesures[4],
                                             io).encode("utf-8"))

    # Fermeture du fichier valeurs
    print("Closing value file...")
    mmvf.close()
    vf.close()
