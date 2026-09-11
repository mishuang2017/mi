#!/usr/local/bin/drgn -k

from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

from lib import prog

def pci_name(pdev):
    try:
        return pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

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

def build_vport_to_netdev_map():
    """Map (esw address, vport_num) -> netdev name for every mlx5e rep netdev."""
    m = {}
    try:
        rep_ops_addr = prog['mlx5e_rep_netdev_ops'].address_of_().value_()
    except KeyError:
        rep_ops_addr = None

    for dev in lib.get_netdevs():
        try:
            if rep_ops_addr is not None and dev.netdev_ops.value_() != rep_ops_addr:
                continue
            netdev_name = dev.name.string_().decode('utf-8', errors='replace')
            mlx5e_priv = lib.get_mlx5(dev)
            if not mlx5e_priv.ppriv.value_():
                continue
            rpriv = Object(prog, 'struct mlx5e_rep_priv', address=mlx5e_priv.ppriv.value_())
            rep = rpriv.rep
            esw_addr = mlx5e_priv.mdev.priv.eswitch.value_()
            vport_num = rep.vport.value_()
            m[(esw_addr, vport_num)] = netdev_name
        except Exception:
            continue
    return m

def dump_spfs():
    devs = get_mlx5_core_devs_by_bdf()
    vport_to_netdev = build_vport_to_netdev_map()

    print("=" * 70)
    print("esw_funcs.spfs (satellite PFs) for all mlx5_core_dev")
    print("=" * 70)

    for bdf in sorted(devs.keys()):
        mdev = devs[bdf]

        esw_addr = mdev.priv.eswitch.value_()
        if not esw_addr:
            continue
        esw = mdev.priv.eswitch

        esw_funcs = esw.esw_funcs
        num_spfs = esw_funcs.num_spfs.value_()

        hpf_host_number = esw_funcs.hpf_host_number.value_()
        hpf_pf_num = esw_funcs.hpf_pf_num.value_()

        # HOST_PF vport is 0x0 -- this is the netdev representing the real
        # external host PF (or self, if not ECPF-managed). NOT a satellite.
        hostpf_netdev = vport_to_netdev.get((esw_addr, 0x0), "?")
        esw_mode = esw.mode.value_()
        esw_mode_str = {0: "LEGACY", 1: "OFFLOADS"}.get(esw_mode, "0x%x" % esw_mode)

        print("\npci: %s  mlx5_core_dev: 0x%lx  esw_mode: %s  hostpf_netdev: %s  "
              "hpf_host_number: 0x%x  hpf_pf_num: 0x%x  num_spfs: %d" % (
            pci_name(mdev.pdev), mdev.address_of_().value_(), esw_mode_str, hostpf_netdev,
            hpf_host_number, hpf_pf_num, num_spfs))

        if num_spfs == 0:
            continue

        spfs = esw_funcs.spfs
        for i in range(num_spfs):
            spf = spfs[i]
            vport_num = spf.vport_num.value_()
            vhca_id = spf.vhca_id.value_()
            host_number = spf.host_number.value_()
            pf_num = spf.pf_num.value_()
            controller_num = host_number + 1
            netdev_name = vport_to_netdev.get((esw_addr, vport_num), "?")

            print("  [%d] SATELLITE  netdev: %-12s vport_num: 0x%x  vhca_id: 0x%x  "
                  "host_number: 0x%x  pf_num: 0x%x  controller_num: 0x%x" % (
                i, netdev_name, vport_num, vhca_id, host_number, pf_num, controller_num))

dump_spfs()
