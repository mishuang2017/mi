#!/usr/local/bin/drgn -k

from drgn.helpers.linux.pid import for_each_task
from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from drgn import cast

import subprocess
import drgn
import sys
import time

sys.path.append("..")
from lib import *

uverbs_event_fops = prog['uverbs_event_fops'].address_of_().value_()
uverbs_mmap_fops = prog['uverbs_mmap_fops'].address_of_().value_()

def print_files(files, n):
    for i in range(n):
        file = files[i]

        if not file.value_():
            continue
#         print("file: %lx" % file)
        if file.f_op.value_() != uverbs_mmap_fops:
            continue

        print("%2d" % i, end='\t')
        print(file.f_op)
        print("inode: %lx" % file.f_inode)

        ib_uverbs_device = container_of(file.f_inode.i_cdev, "struct ib_uverbs_device", "cdev")
        print(ib_uverbs_device.dev.kobj.name)

        for ib_uverbs_file in list_for_each_entry('struct ib_uverbs_file', ib_uverbs_device.uverbs_file_list.address_of_(), 'list'):
            print(ib_uverbs_file)
            for node in radix_tree_for_each(ib_uverbs_file.idr.address_of_()):
                ib_uobject = Object(prog, 'struct ib_uobject', address=node[1].value_())
                print("-----------------------------")
                print("ib_uobject.id: %d" % ib_uobject.id)
                if ib_uobject.id == 5:
                    ib_qp = Object(prog, 'struct ib_qp', address=ib_uobject.object)
#                     print(ib_qp)
                    mlx5_ib_qp = container_of(ib_qp.real_qp, "struct mlx5_ib_qp", "ibqp")
                    print(mlx5_ib_qp.port)
                    print(mlx5_ib_qp.ibqp.res.type)
                if ib_uobject.id == 3:
                    ib_cq = Object(prog, 'struct mlx5_ib_cq', address=ib_uobject.object)
                    print(ib_cq.ibcq.res.type)
                if ib_uobject.id == 2:
                    ib_pd = Object(prog, 'struct mlx5_ib_pd', address=ib_uobject.object)
                    print(ib_pd.ibpd.res.type)
                if ib_uobject.id == 9:
                    ib_mr = Object(prog, 'struct mlx5_ib_mr', address=ib_uobject.object)
                    print(ib_mr.ibmr.res.type)
#                 ib_uqp_object = Object(prog, 'struct ib_uqp_object', address=node[1].value_())
#                 print(ib_uqp_object)
#                 print(ib_uqp_object.uevent.uobject.object)
#                 if prog['IB_QPT_RC'] == ib_qp.qp_type:
#                     print(mlx5_ib_qp)
#                 print(ib_uobject.uapi_object.type_attrs)
#                 print(ib_uobject.uapi_object.type_class)

#             print(ib_uverbs_file.dev.kobj.name)

#         uapi = ib_uverbs_device.uapi
#         print(uapi)
#         for node in radix_tree_for_each(uapi.radix.address_of_()):
#             uverbs_api_object = Object(prog, 'struct uverbs_api_object', address=node[1].value_())

def find_task(name):
    print('PID        COMM')
    for task in for_each_task(prog):
        pid = task.pid.value_()
        comm = task.comm.string_().decode()
        if comm == name:
            print(f'{pid:<10} {comm}')
            return task

task = find_task("rdma_client")
fdt = task.files.fdt
print_files(fdt.fd, fdt.max_fds)
