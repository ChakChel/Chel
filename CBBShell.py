#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@file    CBBShell.py
@author  PERROCHAUD Clément
@version 1.5
@date    2013-11-05

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

HOSTAPD_CONFIG = "/etc/hostapd.conf"

# GLOBALES #####################################################################

cmdDict = {}

mmvf = None

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

def hostapdConfig(parameter, value):

    hapdConf = open(HOSTAPD_CONFIG, "r")
    configLines = hapdConf.readlines()
    hapdConf.close()

    for i, line in enumerate(configLines):
        configLines[i] = re.sub(r"{}=.*\n".format(parameter),
                                "{}={}\n".format(parameter, value),
                                line)

    hapdConf = open(HOSTAPD_CONFIG, "w")
    hapdConf.writelines(configLines)
    hapdConf.close()

def cmdChannel(args):
    
    if len(args) < 2:
        return "Error: No value given"

    hostapdConfig("channel", args[1])

    return "Channel updated"

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
        if not line:
            break
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

    if len(args[1]) < 8:
        return "Error: Password too short"

    proc = sp.Popen(["/usr/bin/sudo",
                     "/usr/bin/passwd",
                     "chel"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    proc.stdin.write("{}\n{}\n".format(args[1], args[1]))

    if proc.wait():
        return "Error: Failed to change password"

    hostapdConfig("wpa_passphrase", args[1])

    return "Password updated"

def cmdSsid(args):
    
    if len(args) < 2:
        return "Error: No value given"

    hostapdConfig("ssid", args[1])

    return "SSID updated"

def cmdWifi(args):

    if len(args) < 2:
        return "Error: No command given"

    if args[1] not in ("start", "stop", "restart"):
        return "Error: Invalid command"

    for service in ("hostapd", "initWifi", "udhcpd"):
        proc = sp.Popen(["/usr/bin/sudo",
                         "/bin/systemctl",
                         args[1],
                         service],
                        stdin=sp.PIPE,
                        stdout=sp.PIPE,
                        stderr=sp.STDOUT)
        if proc.wait():
            return "Error: Failed to change WiFi status"
    
    return "WiFi status updated"

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
                                "Start/Stop/Restart WiFi access point"),
               "channel": Commande(cmdChannel,
                                   "Update WiFi channel"),
               "ssid": Commande(cmdSsid,
                                "Update WiFi SSID")}
    while True:
        try:
            cmd = input(INVITE).split(" ")
        except EOFError:
            break
        if cmd[0] in cmdDict.keys():
            print(cmdDict[cmd[0]].action(cmd))
        elif len(cmd[0]):
            print("Error: Enter help to know the supported commands")

    print("\nInterrupted, exiting...")
    mmvf.close()
    vf.close()
