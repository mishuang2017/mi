#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os
import struct as _struct

sys.path.append(".")
from lib import *

devices   = prog['devices']
rdma_nets = prog['rdma_nets']

init_net_addr = prog['init_net'].address_of_().value_()

# Build map: net_addr -> netns display name using rdma_nets xarray
# rdma_nets xarray key matches 'ip netns list' (id: N)
# Try to also read the name from /var/run/netns via net inum
netns_map = {}  # net_addr -> name
for node in radix_tree_for_each(rdma_nets.address_of_()):
    rnet_id  = node[0]
    rnet_ptr = node[1].value_()
    if not rnet_ptr:
        continue
    try:
        rnet = Object(prog, 'struct rdma_dev_net', address=rnet_ptr)
        net_addr = rnet.net.net.value_()
        # Try to get the namespace name from its inum via /var/run/netns
        net_obj = Object(prog, 'struct net', address=net_addr)
        try:
            inum = net_obj.ns.inum.value_()
            # Match against /var/run/netns symlinks by inum
            ns_name = None
            ns_dir = "/var/run/netns"
            if os.path.isdir(ns_dir):
                for entry in os.listdir(ns_dir):
                    path = os.path.join(ns_dir, entry)
                    try:
                        if os.stat(path).st_ino == inum:
                            ns_name = entry
                            break
                    except Exception:
                        pass
            netns_map[net_addr] = ns_name if ns_name else ("id:%d" % rnet_id)
        except Exception:
            netns_map[net_addr] = "id:%d" % rnet_id
    except Exception:
        pass

# Find byte offset of rdma_net pointer in struct ib_device by scanning
# for init_net address in the first device's memory
rdma_net_offset = None
for node in radix_tree_for_each(devices.address_of_()):
    dev_ptr = node[1].value_() & ~0x3
    try:
        raw = prog.read(dev_ptr, 8192)
        init_bytes = _struct.pack('<Q', init_net_addr)
        idx = raw.find(init_bytes)
        if idx >= 0:
            rdma_net_offset = idx
    except Exception:
        pass
    break  # only need first device

print("%-20s %-6s %-16s %s" % ("ib_device", "index", "netns", "name"))
print("-" * 64)

for node in radix_tree_for_each(devices.address_of_()):
    xa_idx  = node[0]
    dev_ptr = node[1].value_() & ~0x3

    # Read device name at confirmed offset 1200
    try:
        raw = prog.read(dev_ptr + 1200, 64)
        dev_name = raw.split(b'\x00')[0].decode('ascii', errors='replace')
    except Exception:
        dev_name = "<unknown>"

    # Read rdma_net pointer at scanned offset
    netns_name = "unknown"
    if rdma_net_offset is not None:
        try:
            raw = prog.read(dev_ptr + rdma_net_offset, 8)
            net_addr = _struct.unpack('<Q', raw)[0]
            if net_addr == init_net_addr:
                netns_name = "init_net"
            elif net_addr in netns_map:
                netns_name = netns_map[net_addr]
            else:
                netns_name = "net:0x%x" % net_addr
        except Exception:
            netns_name = "exc"

    print("0x%-18x %-6d %-16s %s" % (dev_ptr, xa_idx, netns_name, dev_name))
