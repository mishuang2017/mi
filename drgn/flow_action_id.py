#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

# 12
FLOW_ACTION_TUNNEL_DECAP = prog['FLOW_ACTION_TUNNEL_DECAP']
print("FLOW_ACTION_TUNNEL_DECAP: %d" % FLOW_ACTION_TUNNEL_DECAP)

FLOW_ACTION_TUNNEL_ENCAP = prog['FLOW_ACTION_TUNNEL_ENCAP']
print("FLOW_ACTION_TUNNEL_ENCAP: %d" % FLOW_ACTION_TUNNEL_ENCAP)

# 5
FLOW_ACTION_MIRRED = prog['FLOW_ACTION_MIRRED']
print("FLOW_ACTION_MIRRED: %d" % FLOW_ACTION_MIRRED)

# 13
FLOW_ACTION_MANGLE = prog['FLOW_ACTION_MANGLE']
print("FLOW_ACTION_MANGLE: %d" % FLOW_ACTION_MANGLE)

# 4
FLOW_ACTION_REDIRECT = prog['FLOW_ACTION_REDIRECT']
print("FLOW_ACTION_REDIRECT: %d" % FLOW_ACTION_REDIRECT)

# 22
FLOW_ACTION_SAMPLE = prog['FLOW_ACTION_SAMPLE']
print("FLOW_ACTION_SAMPLE: %d" % FLOW_ACTION_SAMPLE)
