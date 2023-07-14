#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

psample_sock = prog['psample_sock']
print("\n===psample_sock===")
print(psample_sock)

# xbridge = get_xbridge("br")
# print(xbridge)

ofproto_dpif = get_ofproto_dpif("br1")

# in set_sflow()
#   ofproto->sflow = dpif_sflow_create();
sflow = ofproto_dpif.sflow
if sflow.value_() == 0:
    print("no sFlow")
    exit(0)
print(sflow)

sflow_ports = print_hmap(sflow.ports.address_of_(), "dpif_sflow_port", "hmap_node")
for i, sflow_port in enumerate(sflow_ports):
    print("------------------ sflow_port ----------------------")
    print(sflow_port)
    print("sflow port odp_port: %d, dsi.ds_index: %d" % (sflow_port.odp_port, sflow_port.dsi.ds_index))
print('')

collectors = sflow.collectors
print(collectors)
for j in range(collectors.n_fds):
    print("collectors.fds[%d] = %d" % (j, collectors.fds[j]))
print('')

print("=== sflow.sflow_agent ===")
print(sflow.sflow_agent)
# print("sflow.sflow_agent.samplers.flowSampleSeqNo: %d" % sflow.sflow_agent.samplers.flowSampleSeqNo)

# sflow_agent_send_packet_cb
# print(sflow.sflow_agent.samplers.agent.sendFn)

print("=== sflow.sflow_agent.samplers ===")
print(sflow.sflow_agent.samplers)
print(sflow.sflow_agent.samplers.myReceiver)
print('')

options = sflow.options
# print(options)
targets = sflow.options.targets
ssets = print_hmap(targets.map, "sset_node", "hmap_node")
for k, sset in enumerate(ssets):
    print("sflow.options.targets: %s" % sset.name[0].address_of_().string_().decode())
print("sflow.options.sampling_rate: %d, polling_interval: %d, header_len: %d, agent_device: %s" % \
    (options.sampling_rate, options.polling_interval, options.header_len, options.agent_device.string_().decode()))
