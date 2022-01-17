#
# Makefile for the complete.c
#

obj-m := complete.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = complete.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod complete
	-sudo dmesg -CT

run:
	-mknod /dev/complete c 160 0
	-sudo insmod ./complete.ko
	-sudo dmesg -T
