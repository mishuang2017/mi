# builds the kprobes example kernel modules;
# then to use one (as root):  insmod <module_name.ko>

obj-m := kprobe_example.o jprobe_example.o
obj-m := kretprobe_example.o
CURRENT_PATH := $(shell pwd)
KERNEL_SRC :=/home/mishuang/linux-4.1.37

all: 
	$(MAKE) -C $(KERNEL_SRC) M=$(CURRENT_PATH) modules

clean:  
	rm *.ko
	rm *.o

