#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import cast
import subprocess
import socket
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

(status, output) = subprocess.getstatusoutput("grep -w dev_table /proc/kallsyms | grep openvswitch | awk '{print $1}'")
print("%d, %s" % (status, output))

if status:
    sys.exit(1)

t = int(output, 16)
p = Object(prog, 'struct hlist_head *', address=t)

for i in range(1024):
    for vport in hlist_for_each_entry('struct vport', p, 'hash_node'):
        name = vport.dev.name.string_().decode()
        port_no = vport.port_no
        upcall_portids = vport.upcall_portids
        ids = upcall_portids.ids
        id = ids[0]
        print("name: %10s,  n_ids: %d, id: %x" % (name, upcall_portids.n_ids, id))
        print("vport %lx" % vport)
        print("datapath %lx" % vport.dp)
        print("vport_portids %lx" % upcall_portids)
        print("vport_no %d" % port_no)
        print("")
    p = p + 1

table = vport.dp.table
# print(table)
ufid_count = table.count.value_()
ufid_ti = table.ufid_ti
print("ufid_count: %d" % ufid_count)
# print(ufid_ti)
buckets = ufid_ti.buckets
# print(buckets)
element_size = buckets.element_size
total_nr_elements = buckets.total_nr_elements
elems_per_part = buckets.elems_per_part
num = total_nr_elements / elems_per_part
print("num: %d" % num)

n_buckets = ufid_ti.n_buckets.value_()
node_ver = ufid_ti.node_ver.value_()
print("n_buckets: %d, node_ver: %d" % (n_buckets, node_ver))

def print_mac(mac):
    a = ("%02x:%02x:%02x:%02x:%02x:%02x") % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])
    return a

def print_eth(eth):
    print("eth: ", end='')
    type = eth.type
    print("type: %4x, src: %s, dst: %s" % (socket.ntohs(type), print_mac(eth.src), print_mac(eth.dst)))

def print_flow_key(key):
#     MAC_PROTO_ETHERNET = 1
#     mac_proto = key.mac_proto
#     print(mac_proto)
    print_eth(key.eth)
    proto = key.ip.proto.value_()
    print("proto: %d, src: %s" % (proto, lib.ipv4(socket.ntohl(key.ipv4.addr.src.value_()))))
    tp_dst = key.tp.dst
    print("tp_dst: %d" % socket.ntohs(tp_dst))

def print_flow_act(acts):
    nlattr = acts.actions[0]
    nla_type = nlattr.nla_type
    if nla_type == prog['OVS_ACTION_ATTR_OUTPUT']:
        addr = nlattr.address_of_().value_() + prog.type('struct nlattr').size
        port = Object(prog, 'int', address=addr)
        print("\toutput port: %d" % port.value_())

def print_flow_stat(stat):
    print("\tpacket_count: %d" % stat[0].packet_count)

if lib.kernel("4.19.36+") == False:
    for i in range(n_buckets):
        for flow in hlist_for_each_entry('struct sw_flow', ufid_ti.buckets[i].address_of_(), 'ufid_table'):
            print_flow_key(flow.key)
else:
    for i in range(num):
        array = buckets.parts[i].value_()
        print("\narray %d: %lx" % (i, array))
        for j in range(elems_per_part):
            head = Object(prog, 'struct hlist_head', address=array)
            for flow in hlist_for_each_entry('struct sw_flow', head.address_of_(), 'ufid_table'):
                print("")
                print_flow_key(flow.key)
                print_flow_act(flow.sf_acts)
                print_flow_stat(flow.stats)
            array = array + element_size
