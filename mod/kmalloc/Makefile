#
# Makefile for the kmalloc.c
#

obj-m := kmalloc.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = kmalloc.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod kmalloc
	-sudo dmesg -C

run:
	-sudo insmod ./kmalloc.ko
	-sudo dmesg
