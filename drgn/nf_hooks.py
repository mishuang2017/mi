#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

net = prog['init_net']
nf = net.nf
print(nf)

# 0: NT_INET_PRE_ROUTING
#   1: ipv4_conntrack_defrag
#   2: ipv4_conntrack_in
# 1: NF_INET_LOCAL_IN
#   1: ipv4_confirm
# 2: NF_INET_FORWARD
#   1: selinux_ipv4_forward
# 3: NF_INET_LOCAL_OUT
#   1: ipv4_conntrack_defrag
#   2: selinux_ipv4_output
#   3: ipv4_conntrack_local
# 4: NF_INET_POST_ROUTING
#   1: selinux_ipv4_postroute
#   2: ipv4_confirm

enum = {}
enum[0] = "NT_INET_PRE_ROUTING"
enum[1] = "NF_INET_LOCAL_IN"
enum[2] = "NF_INET_FORWARD"
enum[3] = "NF_INET_LOCAL_OUT"
enum[4] = "NF_INET_POST_ROUTING"

ipv4 = nf.hooks_ipv4

for i in range(5):
    print("%d: %s" % (i, enum[i]))
    entry = ipv4[i]
    num = entry.num_hook_entries
    for i in range(num):
        hook = entry.hooks[i].hook
        print("  %d: %s" % (i + 1, lib.address_to_name(hex(hook))))
