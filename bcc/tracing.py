#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb
import commands
import argparse
import sys

parser = argparse.ArgumentParser(description='/sys/kernel/debug/tracing/events')
parser.add_argument("-c", "--command")

args = parser.parse_args()

# load BPF program
b = BPF(text="""
TRACEPOINT_PROBE(net, net_dev_xmit) {
    // args is from /sys/kernel/debug/tracing/events/net/net_dev_xmit/format
    bpf_trace_printk("%d\\n", args->len);
    return 0;
}
""")

if args.command:
    cmd="pgrep " + args.command
    (status, output) = commands.getstatusoutput(cmd)
    if status != 0:
        exit(args.command + " not found")

# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "LEN"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        exit()
    if args.command:
        if pid == int(output):
            printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
    else:
        printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
