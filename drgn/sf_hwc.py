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


def get_mlx5_core_devs_by_bdf():
    """Like lib.get_mlx5_core_devs(), but keyed by full PCI BDF string.
    lib.get_mlx5_core_devs() keys by pci_name.split('.')[1] (function
    number only), which collides across PCI domains on Socket-Direct
    systems (e.g. 0002:01:00.0 and 0006:01:00.0 both hash to key 0),
    silently dropping devices.
    """
    from drgn.helpers.linux import list_for_each_entry

    devs = {}
    subsys_private = lib.get_subsys_private("pci")
    k_list = subsys_private.klist_devices.k_list

    for dev in list_for_each_entry('struct device_private',
                                   k_list.address_of_(), 'knode_bus.n_node'):
        device_private = Object(prog, 'struct device_private', address=dev.value_())
        device = device_private.device
        driver_data = device.driver_data
        if not driver_data.value_():
            continue
        driver = device.driver
        if driver.name.string_().decode() != "mlx5_core":
            continue
        bdf = device.kobj.name.string_().decode()
        devs[bdf] = Object(prog, 'struct mlx5_core_dev', address=driver_data)
    return devs


def dump_sf_hwc():
    devs = get_mlx5_core_devs_by_bdf()

    print("=" * 70)
    print("SF hw_table (hwc buckets) + allocated SFs for all mlx5_core_dev")
    print("=" * 70)

    for bdf in sorted(devs.keys()):
        mdev = devs[bdf]

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

            usr_sfnum = "?"
            if hwc_idx is not None:
                try:
                    usr_sfnum = "%d" % hwc[hwc_idx].sfs[sw_id].usr_sfnum.value_()
                except Exception:
                    usr_sfnum = "?"

            print("  sf: function_id(xa key): 0x%x  sw_id: 0x%x  hw_fn_id: 0x%x  "
                  "controller: 0x%x  pf_num: 0x%x  usr_sfnum: %s  state: %s  -> hwc: %s" % (
                      fn_id, sw_id, hw_fn_id, controller, pf_num, usr_sfnum,
                      VHCA_STATE.get(hw_state, "0x%x" % hw_state), hwc_str))
            printed_any = True

        if not printed_any:
            print("  (no SFs allocated)")


dump_sf_hwc()
