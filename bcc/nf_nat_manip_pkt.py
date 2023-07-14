#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
import socket

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/skbuff.h>

void trace_completion(struct pt_regs *ctx, struct sk_buff *skb) {
    bpf_trace_printk("%llx\\n", skb->dev);
}
""")

b.attach_kprobe(event="nf_nat_manip_pkt", fn_name="trace_completion")

# header
print("%-18s %-2s" % ("TIME(s)", "ETHER_TYPE"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        (bytes_s) = msg.split()

        print("%-18.9f %s" % (ts, bytes_s[0]))
    except KeyboardInterrupt:
        exit()
