#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

console_drivers = prog['console_drivers']

while console_drivers:
    print(console_drivers)
    print(console_drivers.name)
    print(console_drivers.index)

    console_drivers = console_drivers.next
