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
import getopt

sys.path.append("..")
from lib import *

uverbs_event_fops = prog['uverbs_event_fops'].address_of_().value_()
uverbs_mmap_fops = prog['uverbs_mmap_fops'].address_of_().value_()
ucma_fops = prog['ucma_fops'].address_of_().value_()

def print_ib_uverbs(file):
    ib_uverbs_device = container_of(file.f_inode.i_cdev, "struct ib_uverbs_device", "cdev")
    print(ib_uverbs_device.dev.kobj.name)

    uapi = ib_uverbs_device.uapi
#     print(uapi)
#     for node in radix_tree_for_each(uapi.radix.address_of_()):
#         uverbs_api_object = Object(prog, 'struct uverbs_api_object', address=node[1].value_())

    for ib_uverbs_file in list_for_each_entry('struct ib_uverbs_file', ib_uverbs_device.uverbs_file_list.address_of_(), 'list'):
        # print(ib_uverbs_file)
        # print(ib_uverbs_file.ucontext)

        for node in radix_tree_for_each(ib_uverbs_file.idr.address_of_()):
            ib_uobject = Object(prog, 'struct ib_uobject', address=node[1].value_())
            print("-----------------------------")
            print("ib_uobject.id: %d" % ib_uobject.id)

            type_attrs = ib_uobject.uapi_object.type_attrs
            type = container_of(type_attrs, "struct uverbs_obj_idr_type", "type")
            print(address_to_name(hex(type.destroy_object.value_())))

            if address_to_name(hex(type.destroy_object.value_())) == "uverbs_free_cq":
                ib_cq = Object(prog, 'struct mlx5_ib_cq', address=ib_uobject.object)
                print(ib_cq.ibcq.res.type)
                print("ib_cq.ibcq.cqe: %d" % ib_cq.ibcq.cqe)
                print("ib_cq.mcq.cqn: %d" % ib_cq.mcq.cqn)
                print("ib_cq.mcq.irqn: %d" % ib_cq.mcq.irqn)
                print("ib_cq.mcq.pid: %d" % ib_cq.mcq.pid)
                print("ib_cq.cqe_size: %d" % ib_cq.cqe_size)
            if address_to_name(hex(type.destroy_object.value_())) == "uverbs_free_qp":
                ib_qp = Object(prog, 'struct ib_qp', address=ib_uobject.object)
                print(ib_qp.res.type)
                print("ib_qp: %x" % ib_uobject.object)
                print("ib_qp.qp_type: %x" % ib_qp.qp_type)
                print("qp_num: %d, %#x" % (ib_qp.qp_num, ib_qp.qp_num))
                mlx5_ib_qp = container_of(ib_qp.address_of_(), "struct mlx5_ib_qp", "ibqp")
#                 print(mlx5_ib_qp)
            if address_to_name(hex(type.destroy_object.value_())) == "uverbs_free_pd":
                ib_pd = Object(prog, 'struct mlx5_ib_pd', address=ib_uobject.object)
                print(ib_pd.ibpd.res.type)
                print("ib_pd: %x" % ib_uobject.object)
            if address_to_name(hex(type.destroy_object.value_())) == "uverbs_free_mr":
                ib_mr = Object(prog, 'struct mlx5_ib_mr', address=ib_uobject.object)
                print(ib_mr.ibmr.res.type)
                print("ib_mr.ibmr.pd: %x" % ib_mr.ibmr.pd)
                print("ib_mr.ibmr.length: %d" % ib_mr.ibmr.length)
                print("ib_mr.umem.address: %#x" % ib_mr.umem.address)
                print("ib_mr.mmkey.key: %#x" % ib_mr.mmkey.key)
                print("ib_mr.access_flags: %x" % ib_mr.access_flags);
            if address_to_name(hex(type.destroy_object.value_())) == "mmap_obj_cleanup":
                mlx5_user_mmap_entry = Object(prog, 'struct mlx5_user_mmap_entry', address=ib_uobject.object)
                print("mlx5_user_mmap_entry.page_idx: %d" % mlx5_user_mmap_entry.page_idx)
                print("mlx5_user_mmap_entry.rdma_entry.npages: %d" % mlx5_user_mmap_entry.rdma_entry.npages)

#                 ib_uqp_object = Object(prog, 'struct ib_uqp_object', address=node[1].value_())
#                 print(ib_uqp_object)
#                 print(ib_uqp_object.uevent.uobject.object)
#                 if prog['IB_QPT_RC'] == ib_qp.qp_type:
#                     print(mlx5_ib_qp)
#                 print(ib_uobject.uapi_object.type_attrs)
#                 print(ib_uobject.uapi_object.type_class)

def print_ucma_file(file):
        ucma_file = file.private_data
        ucma_file = Object(prog, 'struct ucma_file', address=file.private_data)
        print(ucma_file)
        for context in list_for_each_entry('struct ucma_context', ucma_file.ctx_list.address_of_(), 'list'):
            print("user rdma_cm_id address: %x" % context.uid)
            print("backlog: %x" % context.backlog.counter)
            print(context)
#             print(context.cm_id)
            print(context.cm_id.route.addr.src_addr)
            print('-------------------------------------------')

def print_files(files, n):
    for i in range(n):
        file = files[i]

        if not file.value_():
            continue
        print("%2d" % i, end='\t')

#         print("file: %lx" % file)
#         print(file.f_op)
        print("inode: %lx" % file.f_inode)

        if file.f_op.value_() == uverbs_mmap_fops:
            print_ib_uverbs(file)
        elif file.f_op.value_() == ucma_fops:
            print_ucma_file(file)

def find_task(name):
    print('PID        COMM')
    for task in for_each_task(prog):
        pid = task.pid.value_()
        comm = task.comm.string_().decode()
        if comm == name:
            print(f'{pid:<10} {comm}')
            return task

# parse command line options:
try:
    opts, args = getopt.getopt(sys.argv[1:] ,"p:",["program="])
except getopt.GetoptError:
    sys.exit(2)

for o, a in opts:
    if o in ("-p", "--program"):
        program = a
        print(program)

task = find_task(program)
fdt = task.files.fdt
print_files(fdt.fd, fdt.max_fds)
