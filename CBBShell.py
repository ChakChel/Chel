#!/usr/bin/python3

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

ipRegex = re.compile(r"^(((25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2})[.]){3}\
(25[0-5]|2[0-4][0-9]|[10]?[0-9]{1,2})|(([0-9a-f]{0,2}:){5}[0-9a-f]{0,2}))$")

class Commande:
    def __init__(self, action, desc):
        self.action = action
        self.desc = desc

    def action(self, arg):
        return ""

    def getDesc(self):
        return self.desc

def cmdHelp(arg):
    lines = []
    for cmd in cmdDict.keys():
        lines.append("{}\t{}".format(cmd, cmdDict[cmd].getDesc()))
    return "\n".join(lines)

def cmdEth(arg):
    proc = sp.Popen(["/bin/touch", "-A"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to enter Ethernet Mode"
    
    return "Ethernet Mode is running"

def cmdWifi(arg):
    proc = sp.Popen(["/bin/touch", "-A"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to enter WiFi Mode"
    
    return "WiFi Mode is running"

def cmdIp(arg):
    
    if arg is None or not re.match(ipRegex, arg):
        return "Error: Failed value"
    
    proc = sp.Popen(["/sbin/ifconfig", "eth0", arg],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change IP address"
    
    return "IP address value is updated"

def cmdNetmask(arg):
    
    if arg is None or not re.match(ipRegex, arg):
        return "Error: Failed value"

    proc = sp.Popen(["/sbin/ifconfig", "eth0", "netmask", arg],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT)

    if proc.wait():
        return "Error: Failed to change netmask"

    return "Netmask value is updated"

def cmdConfig(arg):
    return ""

def cmdList(arg):
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
        cmd = tuple(s.lower() for s in cmd) + (None,)
        if cmd[0] in cmdDict.keys():
            print(cmdDict[cmd[0]].action(cmd[1]))
        else:
            print("Error: Enter help to know the supported commands")
