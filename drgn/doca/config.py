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


def LIST_HEAD(head):
	return head.lh_first

def LIST_NEXT(elm):
	return elm.next.le_next

def LIST_FOREACH(head):
	devs = []
	var = LIST_HEAD(head)
	while var:
		devs.append(var)
		var = LIST_NEXT(var)
	return devs
dev_ctx_list = prog['dev_ctx_list']
# LIST_FOREACH(dev_ctx_list)

# for x, dev in enumerate(LIST_FOREACH(dev_ctx_list)):
# 	print(dev)
# exit(0)

# phdev_list = prog['phdev_list']
# for x, dev in enumerate(LIST_FOREACH(phdev_list)):
# 	print(dev.ctx)

drivers_list = prog['drivers_list']
print(drivers_list)

devices_list = prog['devices_list']
print(devices_list)

def TAILQ_FIRST(head):
	return head.tqh_first

def TAILQ_NEXT(head):
	return head.next.tqe_next

def TAILQ_FOREACH(head):
	devs = []
	var = TAILQ_FIRST(head)
	while var:
		devs.append(var)
		var = TAILQ_NEXT(var)
	return devs

for x, dev in enumerate(TAILQ_FOREACH(drivers_list)):
	print(dev)

mlx5_glue = prog['mlx5_glue']
# print(mlx5_glue)

# rte_eth_devices = prog['rte_eth_devices']

def get_mlx5_priv(addr, index):
	addr = addr + prog.type('struct rte_eth_dev').size * index
	rte_eth_devices = Object(prog, 'struct rte_eth_dev', address=addr)
	print(rte_eth_devices.data)
	private = rte_eth_devices.data.dev_private
	print(private)
	mlx5_priv = Object(prog, 'struct mlx5_priv', address=private)
	return mlx5_priv

mlx5_priv = get_mlx5_priv(0xfffff783cb80, 0)
print(mlx5_priv)

# rte_pci_bus = prog['rte_pci_bus']
# print(rte_pci_bus.device_list.tqh_first.device)
# print(rte_pci_bus.device_list.tqh_first.device.driver)

# eth_dev_shared_data = prog['eth_dev_shared_data']
# print(eth_dev_shared_data)
