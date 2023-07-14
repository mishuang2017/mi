#!/usr/bin/python

from __future__ import print_function
from bcc import ArgString, BPF
from bcc.utils import printb
import argparse
from datetime import datetime, timedelta
import os

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/device.h>
#include <uapi/linux/limits.h>

BPF_PERF_OUTPUT(events);

struct data_t {
    u64 ts;
    u64 dev;
    char name[NAME_MAX];
};

void trace_completion(struct pt_regs *ctx, struct device *dev) {
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.dev = (u64)dev;
    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), dev->kobj.name);

    events.perf_submit(ctx, &data, sizeof(data));
}
""")

b.attach_kprobe(event="device_add", fn_name="trace_completion")
initial_ts = 0

# header
print("%-17s %-29s %-18s" % ("TIME(s)", "device", "name"))

def print_event(cpu, data, size):
    global initial_ts
    event = b["events"].event(data)

    if not initial_ts:
        initial_ts = event.ts

    delta = event.ts - initial_ts
    print("%-18.2f" % (float(delta) / 1000000), end="")

    print("%-30lx" % event.dev, end="")
    printb(b'%s' % event.name)

# format output
start_time = datetime.now()
b["events"].open_perf_buffer(print_event, page_cnt=64)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
