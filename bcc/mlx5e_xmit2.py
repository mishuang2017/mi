#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb
import socket

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/skbuff.h>

BPF_PERF_OUTPUT(events);

struct data_t {
    u16 protocol;
};

void trace_completion(struct pt_regs *ctx, struct sk_buff *buf) {
    struct data_t data = {};

    data.protocol = buf->protocol;
    events.perf_submit(ctx, &data, sizeof(data));
}
""")

b.attach_kprobe(event="mlx5e_xmit", fn_name="trace_completion")

# header
print("%-18s %-2s" % ("TIME(s)", "ETHER_TYPE"))

def print_event(cpu, data, size):
    event = b["events"].event(data)
    printb(b'%x' % socket.ntohs(int(event.protocol)))

# format output
b["events"].open_perf_buffer(print_event, page_cnt=64)
while 1:
    try:
        b.perf_buffer_poll()

    except KeyboardInterrupt:
        exit()
