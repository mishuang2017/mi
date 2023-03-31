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

dev_ctx_list = prog['dev_ctx_list']
print(dev_ctx_list)

mlx5_dev_ctx_shared = dev_ctx_list.lh_first
# print(mlx5_dev_ctx_shared)

def LIST_HEAD(head):
	return head.lh_first

#define LIST_NEXT(elm, field)   ((elm)->field.le_next)

def LIST_NEXT(elm):
	return elm.next.le_next

def LIST_FOREACH(head):
	var = LIST_HEAD(head)
	while var:
		print(var)
		var = LIST_NEXT(var)
# 		time.sleep(1)
