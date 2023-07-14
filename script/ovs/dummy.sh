#!/bin/bash

function cleanup
{
set -x
	/images/cmi/openvswitch/utilities/ovs-vsctl del-br br0
	/images/cmi/openvswitch/utilities/ovs-vsctl del-br br1

	/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-ofctl exit
	/usr/bin/sleep 0.1
	/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-vswitchd exit --cleanup
	/usr/bin/sleep 0.1
	/images/cmi/openvswitch/utilities/ovs-appctl -t ovsdb-server exit
	/usr/bin/sleep 0.1
	/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-vswitchd exit --cleanup
set +x
}

if [[ $1 == "cleanup" ]]; then
	cleanup
	exit
fi

set -x

/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-ofctl exit
/usr/bin/sleep 0.1
/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-vswitchd exit --cleanup
/usr/bin/sleep 0.1
/images/cmi/openvswitch/utilities/ovs-appctl -t ovsdb-server exit
/usr/bin/sleep 0.1
/images/cmi/openvswitch/utilities/ovs-appctl -t ovs-vswitchd exit --cleanup

/usr/bin/systemctl stop openvswitch.service
/usr/sbin/ip link add veth0 type veth peer name veth1
/usr/sbin/tc qdisc add dev veth0 handle ffff: ingress
/usr/sbin/tc filter add dev veth0 parent ffff: u32 match u32 0 0 police pkts_rate 100 pkts_burst 10
/usr/sbin/ip link del veth0
/usr/lib/systemd/systemd-sysctl --prefix=/net/ipv4/conf/veth1 --prefix=/net/ipv4/neigh/veth1 --prefix=/net/ipv6/conf/veth1 --prefix=/net/ipv6/neigh/veth1
/usr/lib/systemd/systemd-sysctl --prefix=/net/ipv4/conf/veth0 --prefix=/net/ipv4/neigh/veth0 --prefix=/net/ipv6/conf/veth0 --prefix=/net/ipv6/neigh/veth0

/images/cmi/openvswitch/vswitchd/ovs-vswitchd --version
/images/cmi/openvswitch/utilities/ovs-vsctl --version

# /bin/cd /images/cmi/openvswitch/tests/testsuite.dir/0001
/images/cmi/openvswitch/ovsdb/ovsdb-tool create /etc/openvswitch/conf.db /images/cmi/openvswitch/vswitchd/vswitch.ovsschema
# /images/cmi/openvswitch/ovsdb/ovsdb-server --detach --no-chdir --pidfile --log-file --remote=punix:/images/cmi/openvswitch/tests/testsuite.dir/0001/db.sock
/images/cmi/openvswitch/ovsdb/ovsdb-server --detach --no-chdir --pidfile --log-file --remote=punix:/var/run/openvswitch/db.sock
/images/cmi/openvswitch/utilities/ovs-vsctl --no-wait init
/images/cmi/openvswitch/vswitchd/ovs-vswitchd --enable-dummy --disable-system --disable-system-route --detach --no-chdir --pidfile --log-file -vvconn -vofproto_dpif -vunixctl

/images/cmi/openvswitch/utilities/ovs-vsctl del-br br0
/images/cmi/openvswitch/utilities/ovs-vsctl del-br br1

/images/cmi/openvswitch/utilities/ovs-vsctl -- add-br br0 -- set bridge br0 datapath-type=dummy \
	fail-mode=secure other-config:datapath-id=fedcba9876543210 other-config:hwaddr=aa:55:aa:55:00:00 \
	protocols=[OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15]

# /images/cmi/openvswitch/utilities/ovs-vsctl add-br br1 -- set bridge br1 datapath-type=dummy -- \
#     add-port br0 br0p0 -- set Interface br0p0 type=dummy -- \
#     add-port br0 br0p1 -- set Interface br0p1 type=dummy -- \
#     add-port br1 br1p0 -- set Interface br1p0 type=dummy -- \
#     add-port br1 br1p1 -- set Interface br1p1 type=dummy -- \
#     add-port foo bar -- set Interface bar type=dummy

set +x
