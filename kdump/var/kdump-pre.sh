#!/bin/bash

# file /var/crash/scripts/kdump-pre.sh

mount /dev/fedora/var /sysroot

cd /sysroot/crash

id=$(ls vmcore.* | cut -d . -f 2 | tail -1)

if [[ -z $id ]]; then
	id=0
else
	id=$((id+1))
fi

cp /proc/vmcore /sysroot/crash/vmcore.$id
