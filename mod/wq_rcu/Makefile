KVERSION = $(shell uname -r)
obj-m = workQueue.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod workQueue
	-sudo dmesg -C

run:
	-sudo insmod ./workQueue.ko
	-sudo dmesg
