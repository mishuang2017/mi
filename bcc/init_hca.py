#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
import socket

# load BPF program
b = BPF(text="""
#include <linux/pci.h>

BPF_PERF_OUTPUT(events);

struct data_t {
    char name[64];
    u64 ts;
    char pci[64];
    u16 func_id;
    int npages;
};

void kprobe__give_pages(struct pt_regs *ctx, struct pci_dev **dev, u16 func_id, int npages) {
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};
    char name[] = "give_pages";

    data.npages = npages;
    data.func_id = func_id;
    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    bpf_probe_read_str(&data.pci, sizeof(data.pci), (*dev)->dev.kobj.name);

    events.perf_submit(ctx, &data, sizeof(data));
}

void kretprobe__give_pages(struct pt_regs *ctx) {
    char name[] = "give_pages_ret";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);

    events.perf_submit(ctx, &data, sizeof(data));
}

void kprobe__mlx5_cmd_init_hca(struct pt_regs *ctx, struct pci_dev **dev) {
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};
    char name[] = "mlx5_cmd_init_hca";

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    bpf_probe_read_str(&data.pci, sizeof(data.pci), (*dev)->dev.kobj.name);

    events.perf_submit(ctx, &data, sizeof(data));
}

void kretprobe__mlx5_cmd_init_hca(struct pt_regs *ctx) {
    char name[] = "mlx5_cmd_init_hca_ret";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);

    events.perf_submit(ctx, &data, sizeof(data));
}
""")

# header
print("%-25s%-18s%-15s%-10s%-10s" % ("function", "timestamp", "PCI", "func_id", "pages"))

def print_give_pages(cpu, data, size):
    event = b["events"].event(data)
    print("%-25s" % event.name, end="")
    if '_ret' in event.name:
        print("%-18.4f" % (float(event.ts) / 1000000))
    else:
        print("%-18.4f" % (float(event.ts) / 1000000), end="")
        print("%-15s" % event.pci, end="")
        print("%-10d" % event.func_id, end="")
        print('0x%-10lx' % int(event.npages))

# format output
b["events"].open_perf_buffer(print_give_pages, page_cnt=64)
while 1:
    try:
        b.perf_buffer_poll()

    except KeyboardInterrupt:
        exit()
