#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

# crash> list -H intf_list -s mlx5_interface -l mlx5_interface.list
# ffffffffc0af51a8
# struct mlx5_interface {
#   add = 0xffffffffc0a68fa0 <mlx5e_add>,
#   remove = 0xffffffffc0a68ed0 <mlx5e_remove>,
#   attach = 0xffffffffc0a68d70 <mlx5e_attach>,
#   detach = 0xffffffffc0a68e40 <mlx5e_detach>,
#   protocol = 0x1,
#   list = {
#     next = 0xffffffffc0b76028 <mlx5_ib_interface+40>,
#     prev = 0xffffffffc0af3730 <intf_list>
#   }
# }
# ffffffffc0b76028
# struct mlx5_interface {
#   add = 0xffffffffc0b34740 <mlx5_ib_add>,
#   remove = 0xffffffffc0b34600 <mlx5_ib_remove>,
#   attach = 0x0,
#   detach = 0x0,
#   protocol = 0x0,
#   list = {
#     next = 0xffffffffc0af3730 <intf_list>,
#     prev = 0xffffffffc0af51a8 <mlx5e_interface+40>
#   }
# }

devs = lib.get_mlx5_core_devs()
for i in devs.keys():
    dev = devs[i]
    pci_name = dev.device.kobj.name.string_().decode()
    print(pci_name)
    print(dev.coredev_type)
    print("mlx5_core_dev %lx" % dev.address_of_())
    ctx_list = dev.priv.ctx_list

    if i == 0:
        print("mode: %d" % dev.priv.eswitch.mode)
        mode = dev.priv.eswitch.mode

    for ctx in list_for_each_entry('struct mlx5_device_context', ctx_list.address_of_(), 'list'):
        intf = ctx.intf
        print("intf")
        print(intf)
        continue
        name = lib.address_to_name(hex(intf))
        if name == "mlx5_ib_interface":
            print("intf %20s, state: %x, contex: %lx" % (name, ctx.state, ctx.context))
            print(ctx)
            # for legacy mode, context is the pointer of mlx5_ib_dev
            # for switchdev mode, it is mlx5_core_dev
#             if mode.value_() == prog['SRIOV_LEGACY']:
            if mode.value_() == prog['MLX5_ESWITCH_LEGACY']:
                mlx5_ib_dev = Object(prog, 'struct mlx5_ib_dev', address=ctx.context)
                print("mlx5_ib_dev.num_ports: %d" % mlx5_ib_dev.num_ports.value_())
                print("ib_dev.phys_port_cnt: %d" % mlx5_ib_dev.ib_dev.phys_port_cnt.value_())
        if name == "mlx5e_interface":
            print(intf)
    print("")


intf_list = prog['intf_list']
for intf in list_for_each_entry('struct mlx5_interface', intf_list.address_of_(), 'list'):
    add = intf.add
    remove = intf.remove
    attach = intf.attach
    detach = intf.detach
    print("add   : %s" % (lib.address_to_name(hex(add))))
    print("remove: %s" % (lib.address_to_name(hex(remove))))
    print("attach: %s" % (lib.address_to_name(hex(attach))))
    print("detach: %s" % (lib.address_to_name(hex(detach))))
    print(intf)
