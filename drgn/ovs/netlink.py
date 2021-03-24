#!/usr/local/bin/drgn -k

from drgn.helpers.linux.pid import for_each_task
from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from drgn import cast

import subprocess
import drgn
import sys
import time

sys.path.append("..")
from lib import *

print("sk_protocol 16: NETLINK_GENERIC\n")

null_fops = prog['null_fops'].address_of_().value_()
xfs_file_operations = prog['xfs_file_operations'].address_of_().value_()
shmem_file_operations = prog['shmem_file_operations'].address_of_().value_()
pipefifo_fops = prog['pipefifo_fops'].address_of_().value_()

eventpoll_fops = prog['eventpoll_fops'].address_of_().value_()

socket_file_ops = prog['socket_file_ops'].address_of_().value_()
# both netlink_ops and netlink_ops belong to socket
netlink_ops = prog['netlink_ops'].address_of_().value_()
inet_dgram_ops = prog['inet_dgram_ops'].address_of_().value_()

def print_udp_sock(sk):
    inet_sock = cast('struct inet_sock *', sk)
    dest_ip = sk.__sk_common.skc_daddr
    src_ip = sk.__sk_common.skc_rcv_saddr
    dest_port = ntohs(sk.__sk_common.skc_dport)
    src_port = ntohs(inet_sock.inet_sport)
    print("udp socket: dest_ip: %s, src_ip: %s, dest_port: %d, src_port: %d" % \
                (ipv4(ntohl(dest_ip.value_())), ipv4(ntohl(src_ip.value_())), \
                 dest_port, src_port))

def print_netlink_sock(sock):
    print("netlink socket: sock.sk_protocol: %d" % sock.sk.sk_protocol, end='')
    print("\tportid: %10x, %20d" % (sock.portid, sock.portid), end='')
    print("\tdst_portid: %x" % sock.dst_portid, end='')
    print("\tflags: %x" % sock.flags)

def print_eventpoll(file):
    epoll = file.private_data
    epoll = Object(prog, "struct eventpoll", address=file.private_data)
    rb_root = epoll.rbr.rb_root

    print("eventpoll\t", end='')
#     print(epoll)
    for node in rbtree_inorder_for_each_entry("struct epitem", rb_root, "rbn"):
        print("%d" % node.ffd.fd.value_(), end=' ')
        print(node.ffd.file.f_op.poll)
        sock = Object(prog, "struct socket", address=node.ffd.file.private_data)
        print(sock.ops.poll)
    print('')

def print_files(files, n):
    for i in range(n):
        file = files[i]

        print("%2d" % i, end='\t')
        if file.f_op.value_() == eventpoll_fops:
            print_eventpoll(file)
        elif file.f_op.value_() == socket_file_ops:
            sock = Object(prog, "struct socket", address=file.private_data)
            sk = sock.sk
            if sock.ops.value_() == netlink_ops:
                netlink_sock = cast('struct netlink_sock *', sk)
                print_netlink_sock(netlink_sock)
            elif sock.ops.value_() == inet_dgram_ops:
                print_udp_sock(sk)
            else:
                print('')
        elif file.f_op.value_() == pipefifo_fops:
            print('pipefifo_fops')
        elif file.f_op.value_() == null_fops:
            print('null_fops')
        elif file.f_op.value_() == xfs_file_operations:
            print('xfs_file_operations')
        elif file.f_op.value_() == shmem_file_operations:
            print('shmem_file_operations')
        else:
            print(file.f_op)

def find_task(name):
    print('PID        COMM')
    for task in for_each_task(prog):
        pid = task.pid.value_()
        comm = task.comm.string_().decode()
        if comm == "ovs-vswitchd":
            print(f'{pid:<10} {comm}')
            return task

task = find_task("ovs-vswitchd")
next_fd = task.files.next_fd.value_()
open_fds_init = task.files.open_fds_init

fdt = task.files.fdt
# print(fdt)

print_files(fdt.fd, next_fd)
