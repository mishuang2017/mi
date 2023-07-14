#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
import socket

# load BPF program
b = BPF(text="""

BPF_PERF_OUTPUT(events);

struct data_t {
    char name[64];
    u64 ts;
};

void kprobe__mlx5_eswitch_add_offloaded_rule(struct pt_regs *ctx) {
    char name[] = "mlx5_eswitch_add_offloaded_rule";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    events.perf_submit(ctx, &data, sizeof(data));
}

void kretprobe__mlx5_eswitch_add_offloaded_rule(struct pt_regs *ctx) {
    char name[] = "mlx5_eswitch_add_offloaded_rule_ret";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    events.perf_submit(ctx, &data, sizeof(data));
}

void kprobe__mlx5e_configure_flower(struct pt_regs *ctx) {
    char name[] = "mlx5e_configure_flower";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    events.perf_submit(ctx, &data, sizeof(data));
}

void kretprobe__mlx5e_configure_flower(struct pt_regs *ctx) {
    char name[] = "mlx5e_configure_flower_ret";
    u64 tsp = bpf_ktime_get_ns();
    struct data_t data = {};

    data.ts = tsp / 1000;
    bpf_probe_read_str(&data.name, sizeof(data.name), name);
    events.perf_submit(ctx, &data, sizeof(data));
}
""")

# header
print("%-45s%-18s" % ("function", "timestamp"))

def print_mlx5_eswitch_add_offloaded_rule(cpu, data, size):
    event = b["events"].event(data)
    print("%-45s" % event.name, end="")
    if '_ret' in event.name:
        print("%-18.4f" % (float(event.ts) / 1000000))
    else:
        print("%-18.4f" % (float(event.ts) / 1000000))

# format output
b["events"].open_perf_buffer(print_mlx5_eswitch_add_offloaded_rule)
while 1:
    try:
        b.perf_buffer_poll()

    except KeyboardInterrupt:
        exit()
