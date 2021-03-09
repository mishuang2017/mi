#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
import socket

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/device.h>

void trace_completion(struct pt_regs *ctx, struct device *dev) {
    bpf_trace_printk("%llx %s\\n", dev, dev->kobj.name);
}
""")

b.attach_kprobe(event="device_add", fn_name="trace_completion")

# header
print("%-18s %-18s %-18s" % ("TIME(s)", "device", "name"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        (args) = msg.split()

        print("%-18.9f %-18s %-18s" % (ts, args[0], args[1]));
    except KeyboardInterrupt:
        exit()
