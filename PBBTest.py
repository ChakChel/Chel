#!/usr/bin/python
# -*- coding: UTF-8 -*-

# IMPORTS ######################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
import subprocess as sp

import random
import time
import select
import sys

boosts = ([0, 24, 12, 14, 24.2],
          [1, 16, 12, 14, 15.9],
          [2, 36, 22, 24, 36],
          [3, 30, 12, 14, 3.1])

while True:
    for boost in boosts:
        boost[2] += random.gauss(0.0, 0.25)
        boost[3] += random.gauss(0.0, 0.25)
        if boost[3]<boost[2]:
            boost[3] = boost[2]+0.12
        boost[4] = (float(boost[1])+boost[4])/2.0 + random.gauss(0.0, 0.1)
        sys.stdout.write("\t".join([str(x) for x in boost])+"\n")
        sys.stdout.flush()
    time.sleep(0.5)
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().split("\t")
        sys.stdin.flush()
        if len(line) == 2:
            boosts[int(line[0])][1] = int(line[1])
