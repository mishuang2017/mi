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

# static LIST_HEAD(mlx5_dev_ctx_list, mlx5_dev_ctx_shared) dev_ctx_list = LIST_HEAD_INITIALIZER();
# static LIST_HEAD(mlx5_phdev_list, mlx5_physical_device) phdev_list = LIST_HEAD_INITIALIZER();

phdev_list = prog['phdev_list']
# LIST_FOREACH(phdev_list)

for x, dev in enumerate(LIST_FOREACH(phdev_list)):
	print(dev.ctx)
