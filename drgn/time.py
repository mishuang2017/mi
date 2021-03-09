#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

n=0
sum=0

result = {}
for i in range(0,65536):
    result[i] = 0

time = prog['time']
# print(time)
for i in range(0,65536):
    if time[i] and time[i] < 1000:
        n=n+1
        sum=sum+time[i]
#         print("%5d: %d" % (i, time[i]))
        value = result[time[i].value_()]
        result[time[i].value_()] = value + 1

print("n: %d, sum: %d, average: %f" % (n, sum, sum/n))

# print(result)

for k, v in result.items():
    if v:
        print("%3d ms: %d times" % (k, v))
