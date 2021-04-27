#!/bin/bash

function install-packages
{
set -x
	systemctl disable yum-updatesd
	systemctl stop yum-updatesd
	sleep 1
	systemctl disable packagekitd
	systemctl stop packagekitd
	sleep 1

	yum -y update vim-minimal
	sleep 1
	yum -y install vim-enhanced
	sleep 1

	# 'libvirt_driver_storage.so' fails to load due to "undefined symbol: rbd_diff_iterate2"
# 	yum install librbd1-devel
	# pip install requests urllib3 pyOpenSSL --upgrade

	yum -y install virt-manager fence-agents-virsh
	sleep 1
	yum -y install ctags tmux screen ncurses-devel openssl-devel readline-devel snappy-devel wget tcl tcl-devel tk tk-devel git-email bc sysstat libglvnd-glx gcc-c++ bison flex make gdb
	# lzo elf ?
	yum -y install elfutils-libelf-devel

	# install /sbin/installkernel. otherwise, will hit Cannot find LILO error
	yum -y install grubby

	# ofed
	yum -y install gtk2 atk cairo python2-libxml2 createrepo cmake libnl3-devel automake
	yum -y install infiniband-diags.x86_64 ibutils.x86_64
	# dpdk
	yum -y install numactl-devel 

	# ovs

	# tc
	yum -y install libmnl libmnl-devel

	# ovs
	yum -y install openvswitch libcap-ng-devel libatomic libtool dh-autoreconf

        # gdb debug
        # dnf -y debuginfo-install glibc-2.26-15.fc27.x86_64
	# gdb needs makeinfo
	yum -y instal texinfo

	# drgn, xz-devel for lzma
	yum -y install python3-devel dh-autoreconf xz-devel zlib-devel lzo-devel bzip2-devel elfutils-devel

	sleep 1
	systemctl disable gdm
	systemctl stop gdm

	# "cannot find -lnsl", on fedora 31, install libnsl2-devel
	yum -y install libnsl libnsl2-devel
	sleep 1

	# nginx
	yum -y install pcre-devel

	# build rhel 8.3 kernel
	dnf install dwarves
set +x
}

function config-network
{
set -x
	systemctl disable NetworkManager
	systemctl stop NetworkManager
	sleep 1

	# very important to make vxlan work
	systemctl disable firewalld
	systemctl stop firewalld
	dnf -y remove firewalld

	sleep 1
	systemctl enable network
	sleep 1
	systemctl enable kdump
	systemctl start kdump
	sleep 1
set +x
}

set -x
install-packages
# config-network

# sed -i 's/timeout=30/timeout=10/' /lib/systemd/system/NetworkManager-wait-online.service
sleep 1

# very important to make vxlan work
sed -i 's/SELINUX=enforcing/SELINUX=disable/' /etc/selinux/config
setenforce 0

set +x
# http://xmodulo.com/how-to-configure-linux-bridge-interface.html

# netinstall installation source
#	https://mirrors.huaweicloud.com/centos/7/os/x86_64/
#	http://mirror.centos.org/centos/7/os/x86_64/

# sudo EDITOR=vi visudo
# chrism ALL=(ALL) NOPASSWD:ALL


# Trex
function install-trex
{
	install-pip
	pip install pexpect
	yum -y install python-devel
	yum -y install tkinter
	pip install matplotlib

	pip install pyyaml	# for asap test
}

# qalc
yum install -y qalculate
