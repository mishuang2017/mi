#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

xbridge = get_xbridge("br1")

dpif = xbridge.dpif

print(dpif)

print(dpif.dpif_class)
# print(prog['dpif_netlink_class'])

print("\n===dpif_netlink_class===")
print("%30s: %s" % ("get_stats", address_to_name(hex(dpif.dpif_class.get_stats.value_()))))
print("%30s: %s" % ("flow_dump_thread_create", address_to_name(hex(dpif.dpif_class.flow_dump_thread_create.value_()))))
print("%30s: %s" % ("port_add", address_to_name(hex(dpif.dpif_class.port_add.value_()))))
print("%30s: %s" % ("recv", address_to_name(hex(dpif.dpif_class.recv.value_()))))
print("%30s: %s" % ("recv_wait", address_to_name(hex(dpif.dpif_class.recv_wait.value_()))))
# print("%30s: %s" % ("port_get_pid", address_to_name(hex(dpif.dpif_class.port_get_pid.value_()))))
print("%30s: %s" % ("flow_dump_next", address_to_name(hex(dpif.dpif_class.flow_dump_next.value_()))))
print("%30s: %s" % ("operate", address_to_name(hex(dpif.dpif_class.operate.value_()))))

dpif_netlink = container_of(dpif, "struct dpif_netlink" , "dpif")
# print("===dpif_netlink.psample_sock===")
# print(dpif_netlink.psample_sock)
print("===dpif_netlink.port_notifier===")
print(dpif_netlink.port_notifier)

print('')

print("===dpif_handler===")

uc_array_size = dpif_netlink.uc_array_size

n_handlers = dpif_netlink.n_handlers
handlers = dpif_netlink.handlers
for i in range(n_handlers):
    print("handlers[%d]: epoll_fd: %d" % (i, handlers[i].epoll_fd))

    print(handlers[i])
    for j in range(uc_array_size):
        print(handlers[i].epoll_events[j])
    print('===============')
    exit(0)

print('')

print("===dpif_channel ( for each port )===")

channels = dpif_netlink.channels
for i in range(uc_array_size):
    print(channels[i])
    sock = channels[i].sock
#     print(sock)
    print("channels[%d]: fd: %2d, protocol: %d, pid: %x, %d" % \
        (i, sock.fd, sock.protocol, sock.pid, sock.pid))
    print('')

print("===port_notifier===\n")
port_notifier = dpif_netlink.port_notifier
sock = port_notifier
print("port_notifier: fd: %2d, protocol: %d, pid: %x, %d" % \
    (sock.fd, sock.protocol, sock.pid, sock.pid))
