#
# Makefile for the test2.c
#

obj-m := test2.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

KVERSION = $(shell uname -r)
obj-m = test2.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod test2
	-sudo dmesg -C

run:
	-sudo insmod ./test2.ko
	-sudo dmesg
