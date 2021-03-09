#
# Makefile for the rcu_test.c
#

obj-m := rcu_test.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home1/chrism/linux

all:
	$(MAKE) -C $(KERNEL_SRC) M=$(CURRENT_PATH) modules

run:
	-sudo insmod ./rcu_test.ko
	-sudo dmesg

clean:
	-rm *.ko
	-rm *.o
	-rm *.mod.c
	-rm *.order
	-rm *symvers
	-sudo rmmod rcu_test
	-sudo dmesg -C
