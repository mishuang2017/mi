#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import cast
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

def IS_TRIE(n):
    return n.pos >= 32

def IS_TNODE(n):
    return n.bits

def IS_LEAF(n):
    if n.bits:
        return 0
    else:
        return 1

def print_fib(fib):
    trie = fib.tb_data
    print(fib)

    trie = Object(prog, 'struct trie', address=trie)
    print(trie)

    kv = trie.kv
    print(kv)
    print("key_vector %lx" % kv.address_of_())
    print("key_vector %lx" % kv[0].tnode[0].value_())
    print(type(kv))

    for i in range(32):
        if IS_TRIE(kv[i]):
            print("kv[%d] is TRIE" % i)
        if IS_TNODE(kv[i]):
            print("kv[%d] is TNODE" % i)
            print(kv[i])
            print("key[%d]: %x, ip: %s" % (i, kv[i].key, lib.ipv4(socket.ntohl(kv[i].key.value_()))))
            break
        if IS_LEAF(kv[i]):
            print("kv[%d] is LEAF" % i)

    for n in hlist_for_each_entry('struct fib_alias', leaf.address_of_(), 'fa_list'):
        print(n)

ipv4 = prog['init_net'].ipv4
fib_main = ipv4.fib_main
print_fib(fib_main)

trie = cast("struct trie *", fib_main.tb_data)
print(trie)


# kv = Object(prog, 'struct key_vector', address=0xffff8bc2f72f32f0)
# kv = Object(prog, 'struct key_vector', address=0xffff8bc2f72f3350)
# print(kv)
# leaf = kv.leaf

# for alias in hlist_for_each_entry('struct fib_alias', leaf.address_of_(), 'fa_list'):
#     print(alias)
#     print(alias.fa_info)
