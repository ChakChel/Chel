#!/usr/bin/python

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import subprocess as sp
import re

ENTETE = """\
 ****** * * ******* ******     ***    ******    **    ****** ***   ***
*  **** * * *** *** * *** *   *   *  *  ****   *  *   * **** *  *  * *
* *     * *   * *   * *** *  *  *  * * *      * ** *  * *    * * * * *
* *     * *   * *   * ** *   * *** * * *     * **** * * ***  * ** ** *
* *     * *   * *   * * * *  *  *  * * *     * *  * * * *    * * * * *
*  **** * *   * *   * *  * *  *   *  *  **** * *  * * * **** * *  *  *
 ****** * *   * *   * *   * *  ***    ****** * *  * * ****** * *   * *

Citrocaen corp. with Ixchel Intelligent Systems partnership
Boost Converter supervision module interface. Enter help to know the
supported commands\
"""

INVITE = "boost:~# "

ipRegex = re.compile(r"^((((25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2})[.]){3}"
"(25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2}))|(([0-9a-f]{0,2}:){5}[0-9a-f]{0,2}))$")

class Commande:
    def __init__(self, action, desc):
        self.action = action
        self.desc = desc

    def action(self, args):
        return ""

    def getDesc(self):
        return self.desc

def cmdHelp(args):
    lines = []
    for cmd in cmdDict.keys():
        lines.append("{}\t{}".format(cmd, cmdDict[cmd].getDesc()))
    return "\n".join(lines)

def cmdEth(args):
    proc = sp.Popen(["/bin/touch", "-A"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to enter Ethernet Mode"
    
    return "Ethernet Mode is running"

def cmdWifi(args):
    proc = sp.Popen(["/bin/touch", "-A"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to enter WiFi Mode"
    
    return "WiFi Mode is running"

def cmdIp(args):
    
    if (len(args) < 2) or (not re.match(ipRegex, args[1])):
        return "Error: Failed value"
    
    proc = sp.Popen(["/sbin/ifconfig", "eth0", args[1]],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change IP address"
    
    return "IP address value is updated"

def cmdNetmask(args):
    
    if len(args) < 2 or not re.match(ipRegex, args[1]):
        return "Error: Failed value"

    proc = sp.Popen(["/sbin/ifconfig", "eth0", "netmask", args[1]],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change netmask"

    return "Netmask value is updated"

def cmdConfig(args):
    return ""

def cmdList(args):
    return ""

if __name__ == "__main__":
    print(ENTETE)
    cmdDict = {"help": Commande(cmdHelp,
                                "Print supported commands"),
               "eth": Commande(cmdEth,
                               "Start Ethernet Mode and stop WiFi Mode"),
               "wifi": Commande(cmdWifi,
                                "Start WiFi Mode and stop Ethernet Mode"),
               "ip": Commande(cmdIp,
                                "Update IP address value for Ethernet Mode"),
               "netmask": Commande(cmdNetmask,
                                "Update netmask value for Ethernet Mode")}
    while 1:
        cmd = input(INVITE).split(" ")
        if cmd[0] in cmdDict.keys():
            print(cmdDict[cmd[0]].action(cmd))
        else:
            print("Error: Enter help to know the supported commands")
