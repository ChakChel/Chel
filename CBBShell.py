#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    CBBShell.py
@author  PERROCHAUD Clément
@version 1.2
@date    2013-11-01

Shell de configuration du superviseur.
"""

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import subprocess as sp
import re
import mmap
import sys

# CONSTANTES ###################################################################

ENTETE = "Enter help to know the supported commands"

INVITE = "superviseur$ "

IP_REGEX = re.compile(r"^((((25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2})[.]){3}"
"(25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2}))|(([0-9a-f]{0,2}:){5}[0-9a-f]{0,2}))$")

VALUES_FILE = "/tmp/values.chel"

# GLOBALES #####################################################################

cmdDict = {}

# CLASSES ######################################################################

class Commande:
    def __init__(self, action, desc):
        self.action = action
        self.desc = desc

    def action(self, args):
        return ""

    def getDesc(self):
        return self.desc

# FONCTIONS ####################################################################

def cmdConfig(args):

    configStr = ""

    proc = sp.Popen(["/sbin/ifconfig",
                     "eth0"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    configStr += proc.stdout.read()

    proc = sp.Popen(["/sbin/ifconfig",
                     "wlan0"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    configStr += proc.stdout.read()

    proc = sp.Popen(["/sbin/iwconfig",
                     "wlan0"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    configStr += proc.stdout.read()

    return configStr

def cmdHelp(args):
    lines = []
    for cmd in cmdDict.keys():
        lines.append("{}\t{}".format(cmd, cmdDict[cmd].getDesc()))
    return "\n".join(lines)

def cmdIp(args):
    
    if (len(args) < 2) or (not re.match(IP_REGEX, args[1])):
        return "Error: Failed value"
    
    proc = sp.Popen(["/usr/bin/sudo",
                     "/sbin/ifconfig",
                     "eth0",
                     args[1]],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change IP address"

    return "IP address value is updated"

def cmdList(args):
    listStr = "Boost\tCons\tVi\tIi\tPi\tVo\tIo\n"
    mmvf.seek(0)
    while True:
        line = mmvf.readline()
        if line[0:1] == b"#":
            continue
        listStr += line.decode("utf-8")
    return listStr[:-1]

def cmdNetmask(args):
    
    if len(args) < 2 or not re.match(IP_REGEX, args[1]):
        return "Error: Failed value"

    proc = sp.Popen(["/usr/bin/sudo",
                     "/sbin/ifconfig",
                     "eth0",
                     "netmask",
                     args[1]],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change netmask"

    return "Netmask value is updated"

def cmdPasswd(args):
    
    if len(args) < 2:
        return "Error: No password given"

    proc = sp.Popen(["/usr/bin/sudo",
                     "/usr/bin/passwd",
                     "chel"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    proc.stdin.write("{}\n{}\n".format(args[1], args[1]))

    if proc.wait():
        return "Error: Failed to change password"

    return "Password updated"

# TODO !!!
def cmdWifi(args):

    return "Not yet implemented"

#    command = ["/sbin/iwconfig", "wlan0", "mode", "Ad-Hoc", "essid", "Chel"]
#    proc = sp.Popen(["/usr/bin/sudo",
#                     "/sbin/ifconfig",
#                     "wlan0"],
#                    stdin=sp.PIPE,
#                    stdout=sp.PIPE,
#                    stderr=sp.STDOUT)
#
#    if proc.wait():
#        return "Error: Failed to enter WiFi Mode"
#    
#    return "WiFi is now enabled"

# MAIN #########################################################################

if __name__ == "__main__":
    vf = open(VALUES_FILE, "rb")
    mmvf = mmap.mmap(vf.fileno(), 0, access=mmap.ACCESS_READ)
    print(ENTETE)
    cmdDict = {
               "config": Commande(cmdConfig,
                                  "Print current network configuration"),
               "help": Commande(cmdHelp,
                                "Print supported commands"),
               "ip": Commande(cmdIp,
                              "Update IP address value for Ethernet Mode"),
               "list": Commande(cmdList,
                                "List connected modules"),
               "netmask": Commande(cmdNetmask,
                                   "Update netmask value for Ethernet Mode"),
               "passwd": Commande(cmdPasswd,
                                  "Update WiFi and SSH passwords"),
               "wifi": Commande(cmdWifi,
                                "Start/Stop WiFi access point")}
    try:
        while 1:
            cmd = input(INVITE).split(" ")
            if cmd[0] in cmdDict.keys():
                print(cmdDict[cmd[0]].action(cmd))
            elif len(cmd[0]):
                print("Error: Enter help to know the supported commands")
    except EOFError:
        print("\nInterrupted, exiting...")
    mmvf.close()
    vf.close()
