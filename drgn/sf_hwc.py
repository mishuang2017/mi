#!/usr/local/bin/drgn -k

from drgn.helpers.linux.xarray import xa_for_each
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

from lib import prog

HWC_LABELS = {0: "LOCAL", 1: "EXT_HOST"}

VHCA_STATE = {
    0: "INVALID",
    1: "ALLOCATED",
    2: "ACTIVE",
    3: "IN_USE",
    4: "TEARDOWN_REQUEST",
}


def hwc_label(idx):
    if idx in HWC_LABELS:
        return HWC_LABELS[idx]
    return "SPF[%d]" % (idx - 2)


def pci_name(pdev):
    try:
        return pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"


def find_hwc_for_hw_fn_id(hwc, num_hwc, hw_fn_id):
    for i in range(num_hwc):
        start = hwc[i].start_fn_id.value_()
        max_fn = hwc[i].max_fn.value_()
        if start <= hw_fn_id < start + max_fn:
            return i
    return None


def dump_sf_hwc():
    devs = lib.get_mlx5_core_devs()

    print("=" * 70)
    print("SF hw_table (hwc buckets) + allocated SFs for all mlx5_core_dev")
    print("=" * 70)

    for idx in sorted(devs.keys()):
        mdev = devs[idx]

        sf_hw_table = mdev.priv.sf_hw_table
        if not sf_hw_table.value_():
            continue

        print("\npci: %s  mlx5_core_dev: 0x%lx" % (
            pci_name(mdev.pdev), mdev.address_of_().value_()))

        num_hwc = sf_hw_table.num_hwc.value_()
        hwc = sf_hw_table.hwc
        print("  num_hwc: %d" % num_hwc)
        for i in range(num_hwc):
            controller = hwc[i].controller.value_()
            start_fn_id = hwc[i].start_fn_id.value_()
            max_fn = hwc[i].max_fn.value_()
            print("    hwc[%d] %-10s controller: 0x%x  start_fn_id: 0x%x  "
                  "max_fn: %d  range: [0x%x, 0x%x)" % (
                      i, hwc_label(i), controller, start_fn_id, max_fn,
                      start_fn_id, start_fn_id + max_fn))

        sf_table = mdev.priv.sf_table
        if not sf_table.value_():
            continue

        printed_any = False
        for fn_id, entry in xa_for_each(sf_table.function_ids):
            sf = Object(prog, 'struct mlx5_sf', address=entry.value_())
            controller = sf.controller.value_()
            pf_num = sf.pf_num.value_()
            sw_id = sf.id.value_()
            hw_fn_id = sf.hw_fn_id.value_()
            hw_state = sf.hw_state.value_()
            hwc_idx = find_hwc_for_hw_fn_id(hwc, num_hwc, hw_fn_id)
            hwc_str = hwc_label(hwc_idx) if hwc_idx is not None else "??? (no matching hwc range)"

            print("  sf: function_id(xa key): 0x%x  sw_id: 0x%x  hw_fn_id: 0x%x  "
                  "controller: 0x%x  pf_num: 0x%x  state: %s  -> hwc: %s" % (
                      fn_id, sw_id, hw_fn_id, controller, pf_num,
                      VHCA_STATE.get(hw_state, "0x%x" % hw_state), hwc_str))
            printed_any = True

        if not printed_any:
            print("  (no SFs allocated)")


dump_sf_hwc()
