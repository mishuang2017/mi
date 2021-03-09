#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append("..")
import lib

gen = prog['init_net'].gen
id = prog['tcf_action_net_id']
print("tcf_action_net_id: %d" % id)
ptr = gen.ptr[id]
tcf_action_net = Object(prog, 'struct tcf_action_net', address=ptr.value_())
print("tcf_action_net %lx" % tcf_action_net.address_of_())

for cb in list_for_each_entry('struct tcf_action_egdev_cb', tcf_action_net.egdev_list.address_of_(), 'list'):
    print(cb)
    func = cb.cb.value_()
    func = lib.address_to_name(hex(func))
    print(func)
    priv = cb.cb_priv
    priv = Object(prog, 'struct mlx5e_priv', address=priv.value_())
    print(priv.netdev.name.string_().decode())
