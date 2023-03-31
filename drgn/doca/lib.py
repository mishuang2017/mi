#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import socket
from socket import ntohl

import subprocess
import drgn
import sys
import time

def ovs_pid():
    (status, output) = subprocess.getstatusoutput("pgrep doca_flow_drop")

    if status:
        print("ovs is not started")
        sys.exit(1)
    print("ovs pid %d" % int(output))

    return int(output)

prog = drgn.program_from_pid(ovs_pid())
