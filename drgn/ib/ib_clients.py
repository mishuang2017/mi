#!/usr/bin/env drgn
# SPDX-License-Identifier: LGPL-2.1-or-later

"""Dump every registered ``struct ib_client`` on this system.

Walks the static ``clients`` XArray in ``drivers/infiniband/core/device.c``
(where ``ib_register_client()`` stashes each client) and prints each one,
along with the IB devices it is currently attached to.

If multiple ``struct ib_device`` definitions exist in the kernel debug info
(common when the Mellanox OFA backport is loaded alongside inbox headers),
auto-pick the one whose layout matches the running ``ib_core``.

Usage:
    sudo drgn ib_clients.py
"""

import string

from drgn import Object, cast
from drgn.helpers.linux.list import list_for_each_entry
from drgn.helpers.linux.xarray import xa_for_each


CANDIDATE_HEADERS = (
    None,  # default: whichever drgn picks first
    "include/rdma/ib_verbs.h",
    "mlnx-ofa_kernel-4.0/include/rdma/ib_verbs.h",
)
_PRINTABLE = set(string.printable.encode())

# What `ib_set_client_data()` stores for each known client. Use the name from
# the `struct ib_client.name` field as the key. Crash will accept these as
# `<type> <addr>` so the output is copy-paste friendly.
CLIENT_DATA_TYPES = {
    "sa": "struct ib_sa_device",
    "ib_multicast": "struct mcast_device",
    "uverbs": "struct ib_uverbs_device",
    "umad": "struct ib_umad_device",
    "cm": "struct cm_device",
    "ipoib": "struct list_head",
    "cma": "struct cma_device",
    # mad, issm, rdma_cm register with NULL client_data and have no per-device
    # struct.
}


def _looks_like_device_name(b: bytes) -> bool:
    if not b or b[0] == 0:
        return False
    return all(c in _PRINTABLE for c in b)


def _pick_ib_device_type():
    """Return the struct ib_device type whose layout matches a live device."""
    try:
        _, first_dev = next(iter(xa_for_each(prog["devices"].address_of_())))
    except StopIteration:
        return prog.type("struct ib_device")  # no devices to validate against

    addr = first_dev.value_()
    for header in CANDIDATE_HEADERS:
        try:
            t = (
                prog.type("struct ib_device")
                if header is None
                else prog.type("struct ib_device", filename=header)
            )
            obj = Object(prog, t, address=addr)
            name = obj.name.string_()
        except Exception:
            continue
        if _looks_like_device_name(name):
            return t
    raise RuntimeError(
        "No struct ib_device debug-info layout matched the running ib_core; "
        "extend CANDIDATE_HEADERS with the correct path."
    )


def _func_name(fn):
    """Return the symbol name for a function pointer, or the address if unresolved."""
    addr = fn.value_()
    if addr == 0:
        return "(null)"
    try:
        return prog.symbol(addr).name
    except LookupError:
        return hex(addr)


def _dump_ipoib_list(list_head_ptr, indent):
    """The ipoib client_data is a kmalloc'd list_head whose entries are
    struct ipoib_dev_priv {... struct list_head list; ...}.  Print each netdev."""
    head = cast("struct list_head *", list_head_ptr)
    try:
        priv_type = prog.type("struct ipoib_dev_priv")
    except LookupError:
        print(f"{indent}(ipoib module not loaded -- no struct ipoib_dev_priv)")
        return
    for priv in list_for_each_entry(priv_type, head, "list"):
        netdev = priv.dev
        nd_name = netdev.name.string_().decode() if netdev.value_() else "?"
        parent = priv.parent
        parent_name = (
            parent.name.string_().decode() if parent.value_() else "-"
        )
        pkey = int(priv.pkey)
        port = int(priv.port)
        qp = priv.qp.value_()
        qpn = int(priv.qp.qp_num) if qp else 0
        print(
            f"{indent}{nd_name:<12} port={port} pkey=0x{pkey:04x} "
            f"qpn=0x{qpn:06x} parent={parent_name}  "
            f"struct ipoib_dev_priv {hex(priv.value_())}"
        )


def client_devices(client, ibdev_type):
    """Yield (ib_device *, client_data) for each device this client is bound to."""
    client_id = client.client_id.value_()
    for _, dev_void in xa_for_each(prog["devices"].address_of_()):
        if dev_void.value_() == 0:
            continue
        ibdev = Object(prog, ibdev_type, address=dev_void.value_())
        for cid, cdata in xa_for_each(ibdev.client_data.address_of_()):
            if cid == client_id and cdata.value_() != 0:
                yield ibdev, cdata
                break


ibdev_type = _pick_ib_device_type()

print(f"{'id':>3}  {'uses':>4}  {'name':<14} {'ib_client *':<18}  client_data (crash-ready)")
for _, entry in xa_for_each(prog["clients"].address_of_()):
    client = cast("struct ib_client *", entry)
    name = client.name.string_().decode()
    uses = client.uses.refs.counter.value_()
    data_type = CLIENT_DATA_TYPES.get(name, "void")
    pairs = list(client_devices(client, ibdev_type))
    print(
        f"{client.client_id.value_():>3}  {uses:>4}  "
        f"{name:<14} {hex(client.value_()):<18}  struct ib_client {hex(client.value_())}"
    )
    print(f"        add: {_func_name(client.add)}")
    print(f"        remove: {_func_name(client.remove)}")
    if not pairs:
        print(f"        (no devices attached)")
        continue
    for ibdev, data in pairs:
        dev_name = ibdev.name.string_().decode()
        print(
            f"        {dev_name:<10} {data_type} {hex(data.value_())}"
        )
        if name == "ipoib":
            _dump_ipoib_list(data, indent="          ")
