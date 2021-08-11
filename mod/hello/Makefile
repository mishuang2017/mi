#
# Makefile for the helloworld.c
#

obj-m := hello.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/images/cmi/linux

all:
	$(MAKE) -C $(KERNEL_SRC) M=$(CURRENT_PATH) modules

run:
	sudo insmod ./hello.ko
	dmesg | grep hello

clean:
	rm *.ko
	rm *.o
	rm *.mod.c
	rm *.order
	rm *symvers
	sudo rmmod hello
	sudo dmesg -C
