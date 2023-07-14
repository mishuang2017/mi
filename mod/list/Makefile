#
# Makefile for the list.c
#

obj-m := list.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = list.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod list
	-sudo dmesg -C

run:
	-sudo insmod ./list.ko
	-sudo dmesg
