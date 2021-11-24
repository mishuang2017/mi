#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

nf_udp_net = prog['init_net'].ct.nf_ct_proto.udp
print(nf_udp_net)

