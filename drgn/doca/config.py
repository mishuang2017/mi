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
# 	print(rte_eth_devices.data)
	private = rte_eth_devices.data.dev_private
# 	print(private)
	mlx5_priv = Object(prog, 'struct mlx5_priv', address=private)
	return mlx5_priv

def print_mlx5_priv(priv):
	print(priv.rxqs_n)
	print(priv.rxq_privs)
	rxq_privs = Object(prog, 'void *', address=priv.rxq_privs)
	print(rxq_privs)
# 	rxq_privs = Object(prog, 'void *', address=rxq_privs)
# 	print(rxq_privs)
	rxq_priv = Object(prog, 'struct mlx5_rxq_priv', address=rxq_privs)
	print(rxq_priv.ctrl.rxq.stats)
# 	print(priv.sh.groups)

for i in range(2):
	mlx5_priv = get_mlx5_priv(0xfffff783cb80, i)
	print_mlx5_priv(mlx5_priv)

# rte_pci_bus = prog['rte_pci_bus']
# print(rte_pci_bus.device_list.tqh_first.device)
# print(rte_pci_bus.device_list.tqh_first.device.driver)

# eth_dev_shared_data = prog['eth_dev_shared_data']
# print(eth_dev_shared_data)

config1 = prog['config1']
# print(config1.mbuf_pool)
# print(config1.mbuf_pool.elt_list)
# print(config1.mbuf_pool.elt_list.stqh_first)
print(config1)

def get_rte_eth_dev_data(addr, index):
	addr = addr + prog.type('struct rte_eth_dev').size * index
	rte_eth_devices = Object(prog, 'struct rte_eth_dev', address=addr)
	return rte_eth_devices.data

def print_rxq(rxq):
	print(rxq)
	print(rxq.elts_n)
	print(rxq.cqes)
	print(rxq.cq_ci)

data = get_rte_eth_dev_data(0xfffff783cb80, 0)

mlx5_rxq_ctrl = Object(prog, 'struct mlx5_rxq_ctrl', address=data.rx_queues[0])
# print_rxq(mlx5_rxq_ctrl.rxq)
# mlx5_rxq_ctrl = Object(prog, 'struct mlx5_rxq_ctrl', address=data.rx_queues[1])
# print_rxq(mlx5_rxq_ctrl.rxq)

pipe1 = prog['pipe1']
print(pipe1)
# print(pipe1.dpdk_pipe)
print(pipe1.port)
print(pipe1.port.dpdk_port)
print(pipe1.port.dpdk_port.queue_array[0])
print(pipe1.port.dpdk_port.queue_array[1])
