#
# Makefile for the structa.c
#

obj-m := structa.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = structa.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod structa
	-sudo dmesg -C

run:
	-sudo insmod ./structa.ko
	-sudo dmesg
