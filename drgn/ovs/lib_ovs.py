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

def print_hmap(hmap_addr, struct_name, member):
    objs = []

    buckets = hmap_addr.buckets.value_()
    n = hmap_addr.n.value_()

    if n == 0:
        return objs

#     print("\n=== %s: buckets: %x, n: %d ===" % (struct_name, buckets, n))

    i = 0
    while 1:
        p = Object(prog, 'void *', address=buckets)
        if p.value_() == 0:
            buckets = buckets + 8
            continue

        data = container_of(p, "struct " + struct_name, member)
        objs.append(data)

        i += 1
        if i == n:
            return objs

        next = data.member_(member).next

        while next.value_() != 0:

            data = container_of(next, "struct " + struct_name, member)
            objs.append(data)

            i += 1
            if i == n:
                return objs

            next = data.member_(member).next

        buckets = buckets + 8

    return objs

xcfgp = prog['xcfgp']
def get_xbridge(name):
    xbridges_hmap = xcfgp.p.xbridges

    xbridges = print_hmap(xbridges_hmap, "xbridge", "hmap_node")
    for i, xbridge in enumerate(xbridges):

        if xbridge.name.string_().decode() == name:
            return xbridge

# usually there is only one backer named "system"
def get_backer():
    shashes = print_hmap(prog['all_dpif_backers'].map, "shash_node", "node")
    for i, shash in enumerate(shashes):
        if shash.name.string_().decode() == "system":
            backer = Object(prog, 'struct dpif_backer', address=shash.data)
            return backer

def address_to_name(address):
#     print("address: %s" % address)
    (status, output) = subprocess.getstatusoutput("nm /usr/sbin/ovs-vswitchd | grep " + address.strip("0x") + " | awk '{print $3}'")
#     print("%d, %s" % (status, output))

    if status:
        return ""

    return output

def get_ofproto_dpif(name):
    ofprotos = print_hmap(prog['all_ofprotos'], "ofproto", "hmap_node")
    for i, ofproto in enumerate(ofprotos):
        if ofproto.name.string_().decode() == name:
            ofproto_dpif = container_of(ofproto, "struct ofproto_dpif", "up")
            return ofproto_dpif

def print_ufid(ufid):
    print("%x:%x:%x:%x" % \
        (ntohl(ufid.u32[0].value_()), \
         ntohl(ufid.u32[1].value_()), \
         ntohl(ufid.u32[2].value_()), \
         ntohl(ufid.u32[3].value_())))

def print_cmap(cmap, struct_name, member_name):
    objs = []

#     print(cmap.impl.p)
    cmap_impl = cmap.impl.p
    mask = cmap_impl.mask.value_()
#     print("mask: %d" % mask)
    buckets = cmap_impl.buckets
    CMAP_K = 5
    n = 0
    for i in range(mask + 1):
        for j in range(CMAP_K):
            cmap_node = buckets[i].nodes[j].next.p[0]
            if cmap_node.address_of_().value_() == 0:
                continue
#             print(cmap_node)
            data = container_of(cmap_node.address_of_(), "struct " + struct_name, member_name)
            objs.append(data)
            n += 1

    return objs

#     print("n = %d" % n)

def print_seq(seq, name):
    print("%20s: seq value: %d" % (name, seq.value))
    seq_waiters = print_hmap(seq.waiters, "seq_waiter", "hmap_node")
    for i, seq_waiter in enumerate(seq_waiters):
        print(seq_waiter.thread)
        print('')
