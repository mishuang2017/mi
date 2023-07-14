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
from lib import *

flow_pipe = Object(prog, 'struct doca_flow_pipe', address=0xaaaaab069fb0)
print(flow_pipe)
print(flow_pipe.dpdk_pipe)
print(flow_pipe.dpdk_pipe.queues[0])
print(flow_pipe.dpdk_pipe.queues[0].pipe_q.action_ctx.action_entry[0].action)
# print(flow_pipe.dpdk_pipe.queues[1])
# print(flow_pipe.basic_table.table)
# print(flow_pipe.basic_table.table.ats[0])
# print(flow_pipe.basic_table.table.ats[0].acts)
# print(flow_pipe.basic_table.table.ats[0].acts.rule_acts[0])
# print(flow_pipe.basic_table.table.ats[0].acts.rule_acts[0].action)
# print(flow_pipe.basic_table.table.grp)
# print(flow_pipe.basic_table.table.matcher)

# print(flow_pipe.basic_table.table.matcher.mt)
# print(flow_pipe.basic_table.table.matcher.mt.fc)
# print(flow_pipe.basic_table.table.matcher.mt.items)

# print(flow_pipe.basic_table.table.matcher.at)
# print(flow_pipe.basic_table.table.matcher.at.action_type_arr[0])
# print(flow_pipe.basic_table.table.matcher.at.action_type_arr[1])
