#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
import socket

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/skbuff.h>

void trace_completion(struct pt_regs *ctx, struct sk_buff *buf) {
    bpf_trace_printk("%d\\n", buf->protocol);
}
""")

ether_type = {
    0x800: "ETH_P_IP",
    0x806: "ETH_P_ARP"
}

b.attach_kprobe(event="mlx5e_xmit", fn_name="trace_completion")

# header
print("%-18s %-2s" % ("TIME(s)", "ETHER_TYPE"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        (bytes_s) = msg.split()

        type = socket.ntohs(int(bytes_s[0]))
        if ether_type.get(type) == None:
            print("%-18.9f %-7x" % (ts, type))
        else:
            print("%-18.9f %-7s" % (ts, ether_type.get(type)))
    except KeyboardInterrupt:
        exit()
