#!/bin/bash

/sbin/kexec -p '--command-line=BOOT_IMAGE=/boot/vmlinuz-4.16.3-301.fc28.x86_64 ro resume=/dev/mapper/centos-swap intel_iommu=on biosdevname=0 pci=realloc irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never nokaslr disable_cpu_apicid=0' --initrd=/boot/initramfs-4.16.3-301.fc28.x86_64kdump.img /boot/vmlinuz-4.16.3-301.fc28.x86_64
