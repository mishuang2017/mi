#!/usr/bin/env drgn
# SPDX-License-Identifier: LGPL-2.1-or-later

"""Dump all InfiniBand multicast groups on this system.

The ``ib_multicast`` client (``drivers/infiniband/core/multicast.c``) hangs a
``struct mcast_device`` off each IB device via ``ib_set_client_data()``. The
mcast_device has one ``struct mcast_port`` per IB port; each port keeps its
multicast groups in an rbtree at ``port->table`` keyed by MGID.

This script walks: clients XArray -> ib_multicast -> devices XArray ->
mcast_device -> per-port rbtree -> mcast_group, and prints each group with
copy/paste-ready crash addresses.

Usage:
    sudo drgn ib_mcast.py
"""

import socket
import string
import struct

from drgn import Object, cast
from drgn.helpers.linux.rbtree import rbtree_inorder_for_each_entry
from drgn.helpers.linux.xarray import xa_for_each


CANDIDATE_HEADERS = (
    None,
    "include/rdma/ib_verbs.h",
    "mlnx-ofa_kernel-4.0/include/rdma/ib_verbs.h",
)
_PRINTABLE = set(string.printable.encode())

GROUP_STATES = {
    0: "IDLE",
    1: "BUSY",
    2: "GROUP_ERROR",
    3: "PKEY_EVENT",
}


def _looks_like_device_name(b):
    return bool(b) and b[0] != 0 and all(c in _PRINTABLE for c in b)


def _pick_ib_device_type():
    """Pick the struct ib_device whose layout matches the running ib_core."""
    try:
        _, first_dev = next(iter(xa_for_each(prog["devices"].address_of_())))
    except StopIteration:
        return prog.type("struct ib_device")
    addr = first_dev.value_()
    for header in CANDIDATE_HEADERS:
        try:
            t = (
                prog.type("struct ib_device")
                if header is None
                else prog.type("struct ib_device", filename=header)
            )
            if _looks_like_device_name(Object(prog, t, address=addr).name.string_()):
                return t
        except Exception:
            continue
    raise RuntimeError("No struct ib_device layout matched ib_core")


def _gid_str(gid):
    """Format a union ib_gid as ip6-style colon-separated 16-bit words."""
    raw = bytes(gid.raw[i].value_() for i in range(16))
    return ":".join(f"{(raw[i] << 8) | raw[i + 1]:04x}" for i in range(0, 16, 2))


def _be16(obj):
    return socket.ntohs(obj.value_() & 0xFFFF)


def _be32(obj):
    return socket.ntohl(obj.value_() & 0xFFFFFFFF)


def _find_mcast_client():
    for _, entry in xa_for_each(prog["clients"].address_of_()):
        c = cast("struct ib_client *", entry)
        if c.name.string_().decode() == "ib_multicast":
            return c
    return None


def _mcast_devices(client, ibdev_type):
    """Yield (ib_device, mcast_device) for each device the mcast client owns."""
    client_id = client.client_id.value_()
    for _, dev_void in xa_for_each(prog["devices"].address_of_()):
        if dev_void.value_() == 0:
            continue
        ibdev = Object(prog, ibdev_type, address=dev_void.value_())
        for cid, cdata in xa_for_each(ibdev.client_data.address_of_()):
            if cid == client_id and cdata.value_() != 0:
                mdev = Object(prog, "struct mcast_device", address=cdata.value_())
                yield ibdev, mdev
                break


def _dump_group(group, indent):
    rec = group.rec
    mgid = _gid_str(rec.mgid)
    mlid = _be16(rec.mlid)
    qkey = _be32(rec.qkey)
    pkey = _be16(rec.pkey)
    members = [int(group.members[i]) for i in range(len(group.members))]
    state = GROUP_STATES.get(int(group.state), str(int(group.state)))
    refcount = int(group.refcount.counter)
    print(f"{indent}struct mcast_group {hex(group.value_())}")
    print(f"{indent}  mgid           : {mgid}")
    print(f"{indent}  mlid           : 0x{mlid:04x}  ({mlid})")
    print(f"{indent}  qkey           : 0x{qkey:08x}")
    print(f"{indent}  pkey           : 0x{pkey:04x}")
    print(f"{indent}  join_state     : 0x{int(rec.join_state):02x}")
    print(f"{indent}  members[F/N/SN/SF]: {members}")
    print(f"{indent}  state          : {state}")
    print(f"{indent}  refcount       : {refcount}")


def main():
    ibdev_type = _pick_ib_device_type()
    client = _find_mcast_client()
    if client is None:
        print("ib_multicast client not registered")
        return

    any_groups = False
    for ibdev, mdev in _mcast_devices(client, ibdev_type):
        dev_name = ibdev.name.string_().decode()
        start = int(mdev.start_port)
        end = int(mdev.end_port)
        print(f"=== {dev_name}  struct mcast_device {hex(mdev.address_)} "
              f"(ports {start}..{end}) ===")
        for i in range(end - start + 1):
            port = mdev.port[i]
            if port.dev.value_() == 0:
                continue
            port_num = int(port.port_num)
            groups = list(rbtree_inorder_for_each_entry(
                "struct mcast_group", port.table.address_of_(), "node"
            ))
            print(f"  port {port_num}: struct mcast_port {hex(port.address_of_().value_())}  "
                  f"({len(groups)} group{'s' if len(groups) != 1 else ''})")
            for g in groups:
                any_groups = True
                _dump_group(g, "    ")
    if not any_groups:
        print("(no multicast groups joined)")


main()
