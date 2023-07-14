#
# Makefile for the PAGE_OFFSET.c
#

obj-m := PAGE_OFFSET.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = PAGE_OFFSET.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod PAGE_OFFSET
# 	-sudo dmesg -C

run:
	-sudo insmod ./PAGE_OFFSET.ko
	-sudo dmesg
