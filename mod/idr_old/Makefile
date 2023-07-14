#
# Makefile for the idr1.c
#

obj-m := idr1.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

all:
	$(MAKE) -C $(KERNEL_SRC) M=$(CURRENT_PATH) modules

run:
	-sudo insmod ./idr1.ko
	-sudo dmesg

clean:
	-rm *.ko
	-rm *.o
	-rm *.mod.c
	-rm *.order
	-rm *symvers
	-sudo rmmod idr1
	-sudo dmesg -C
