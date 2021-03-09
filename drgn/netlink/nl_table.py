#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
import time
import socket
import sys
import os

sys.path.append("..")
import lib

nl_table = prog['nl_table']
MAX_LINKS = 32

NETLINK_GENERIC = 16
NETLINK_USERSOCK = 2
NETLINK_ROUTE = 0
NETLINK_KOBJECT_UEVENT = 15

# for i in range(MAX_LINKS):
#     print(nl_table[i])

nl_table_16 = nl_table[NETLINK_KOBJECT_UEVENT]
nl_table_16 = nl_table[NETLINK_GENERIC]
# print(nl_table_16.mc_list)
# print(nl_table_16)

for sock in hlist_for_each_entry('struct sock', nl_table_16.mc_list.address_of_(), '__sk_common.skc_bind_node'):
    nsock = container_of(sock, "struct netlink_sock", "sk")
    print("netlink_sock %lx" % nsock)
#     print(nsock)
    print("portid: %10d, %10x, dst_portid: %d, ngroups: %d, group: %d" % \
        (nsock.portid, nsock.portid, nsock.dst_portid, nsock.ngroups, nsock.groups[0]))
#     for i in range(nsock.ngroups):
#         print("%2d: %lx" % (i, nsock.groups[i]))

hash = nl_table_16.hash
# listeners = nl_table[NETLINK_GENERIC].listeners
# print(listeners)

def print_sock(nsock):
    print("\tportid    : %x" % nsock.portid)
#     print("\tdst_portid: %x" % nsock.dst_portid)  # all 0
    sock = nsock.sk
    print("\tsock %lx" % sock.address_of_().value_())
    head = sock.sk_wq.wait.head
    print("\tsk_data_ready: %s" % lib.address_to_name(hex(sock.sk_data_ready)))
    print("")
#     print(head)
    if 1:
        return
    for entry in list_for_each_entry('struct wait_queue_entry', head.address_of_(), 'entry'):
        print("\twait_queue_entry %lx" % entry.value_())
        print("\twait_queue_entry.flags %d" % entry.flags.value_())
        eppoll_entry = container_of(entry, "struct eppoll_entry", 'wait')
        print("\teppoll_entry %lx" % eppoll_entry)
        epitem = eppoll_entry.base
        print("\tepitem %lx" % epitem)
        event = epitem.event
        ffd = epitem.ffd
        print("\tepoll_filefd %lx" % ffd.address_of_().value_())
        if entry.flags.value_():
            print("\tfd: %d" %ffd.fd.value_())
            print("\tfile: %lx" %ffd.file)

            # 10000019
            # EPOLLIN | EPOLLERR | EPOLLHUP | EPOLLWAKEUP
            print("\tevents: %x" % event.events)
            print("\tdata: %x" % event.data)
        func = entry.func
        print("\t%s" % lib.address_to_name(hex(func)))
        print("")

# for i, nsock in enumerate(lib.hash(hash, 'struct netlink_sock', 'node')):
#     print("netlink_sock %lx" % nsock.value_())
#     print_sock(nsock)
