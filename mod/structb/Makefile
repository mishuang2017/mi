#
# Makefile for the structb.c
#

obj-m := structb.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = structb.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod structb
	-sudo dmesg -C

run:
	-sudo insmod ./structb.ko
	-sudo dmesg
