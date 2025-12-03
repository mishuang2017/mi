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
    (status, output) = subprocess.getstatusoutput("pgrep ovs-vswitchd")

    if status:
        print("ovs is not started")
        sys.exit(1)
    print("ovs pid %d" % int(output))

    return int(output)

prog = drgn.program_from_pid(ovs_pid())
# prog = drgn.program_from_core_dump("/tmp/cores/core.revalidator12.1459650.c-141-46-1-010.1631675996");
