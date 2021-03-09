#!/bin/bash

# file /var/crash/scripts/kdump-pre.sh

cd /sysroot/var/crash

id=$(ls vmcore.* | cut -d . -f 2 | tail -1)

if [[ -z $id ]]; then
	id=0
else
	id=$((id+1))
fi

cp /proc/vmcore /sysroot/var/crash/vmcore.$id
