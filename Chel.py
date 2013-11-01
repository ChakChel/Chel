#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    Chel.py
@author  PERROCHAUD Clément
@version 0.8
@date    2013-11-01

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

# MAIN #########################################################################

if __name__ == "__main__":

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

    ### # Démarrage de ABBServer
    ### print("Starting ABBServer...")
    ### abbProc = sp.Popen(["/home/root/Chel/ABBServer.py"],
               ### stdin=sp.PIPE,
               ### stdout=sp.PIPE,
               ### stderr=sys.stderr)
### 
    ### # Démarrage de PBBMaster
    ### print("Starting PBBMaster...")
    ### pbbProc = sp.Popen(["/home/root/Chel/PBBMaster.py"],
               ### stdin=abbProc.stdout,
               ### stdout=sys.stdin,
               ### stderr=sys.stderr)

    print("Writing random stuff ad nauseum...")
    while True:
        mesures = [ int(x) for x in input().split("\t") ]
        mmvf.seek(mesures[0]*41)
        ii = (mesures[3] - mesures[2])/0.055
        pi = mesures[2]*ii
        mmvf.write(FORMAT_REPONSE_ABB.format(mesures[0],
                                             mesures[1],
                                             mesures[2],
                                             ii,
                                             pi,
                                             mesures[4],
                                             pi/mesures[4]).encode("utf-8"))

    # Fermeture du fichier valeurs
    print("Closing value file...")
    mmvf.close()
    vf.close()
