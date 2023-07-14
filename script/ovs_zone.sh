#!/bin/bash

ip netns del test
ip netns add test
ip link add veth1 type veth peer name veth2
ip link set veth1 netns test
ip netns exec test ifconfig veth1 up
ip netns exec test ifconfig veth1 192.168.2.1 netmask 255.255.255.0

#peer=10.238.58.121
ovs-vsctl del-br br0
ovs-vsctl add-br br0
#ovs-vsctl add-port br0 vx$peer -- set interface vx$peer type=vxlan options:remote_ip=$peer option:key=flow
ovs-vsctl add-port br0 veth2
ifconfig veth2 up 
ifconfig veth2 mtu 2000


ip netns del test2
ip netns add test2
ip link add veth3 type veth peer name veth4
ip link set veth3 netns test2
ip netns exec test2 ifconfig veth3 up
ip netns exec test2 ifconfig veth3 192.168.2.2 netmask 255.255.255.0

#peer=10.238.58.121
#ovs-vsctl add-br br0
#ovs-vsctl add-port br0 vx$peer -- set interface vx$peer type=vxlan options:remote_ip=$peer option:key=flow
ovs-vsctl add-port br0 veth4
ifconfig veth4 up 
ifconfig veth4 mtu 2000

VM1_MAC=`ip netns exec test ifconfig | grep ether | cut -d ' ' -f10`
VM1_PORT=1
VM1_IP=192.168.2.1
((VM1_CONJ_ID=($VM1_PORT)))
((VM1_REV_CONJ_ID=($VM1_PORT+500)))

VM2_MAC=`ip netns exec test2 ifconfig | grep ether | cut -d ' ' -f10`
VM2_PORT=2
VM2_IP=192.168.2.2
((VM2_CONJ_ID=($VM2_PORT)))
((VM2_REV_CONJ_ID=($V2_PORT+500)))

iptables -F
ovs-ofctl del-flows br0



ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=0,in_port=$VM1_PORT action=set_field:$VM1_PORT->reg6,goto_table:5"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=0,in_port=$VM2_PORT action=set_field:$VM2_PORT->reg6,goto_table:5"

ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=5,arp action=normal"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=5 action=goto_table:10"

ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=10,ip,reg6=$VM1_PORT actions=ct(table=15,zone=NXM_NX_REG6[0..15])"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=10,ip,reg6=$VM2_PORT actions=ct(table=15,zone=NXM_NX_REG6[0..15])"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=15,ct_state=-new+est-rel-inv+trk actions=goto_table:20"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=15,ct_state=-new+rel-inv+trk actions=goto_table:20"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=15,ct_state=+new+rel-inv+trk,ip actions=ct(commit,table=20,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=15,ct_state=+inv+trk,ip actions=set_field:0x96->reg8,goto_table:200"

ovs-ofctl add-flow br0 -O openflow13 "priority=1000 table=15,conj_id=$VM1_CONJ_ID,ip,reg6=$VM1_PORT actions=ct(commit,table=20,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=15,ct_state=+new-est-rel-inv+trk,reg6=$VM1_PORT actions=conjunction($VM1_CONJ_ID,1/2)"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=15,ip,reg6=$VM1_PORT actions=conjunction($VM1_CONJ_ID,2/2)"

ovs-ofctl add-flow br0 -O openflow13 "priority=1000 table=15,conj_id=$VM2_CONJ_ID,ip,reg6=$VM2_PORT actions=ct(commit,table=20,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=15,ct_state=+new-est-rel-inv+trk,reg6=$VM2_PORT actions=conjunction($VM2_CONJ_ID,1/2)"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=15,ip,reg6=$VM2_PORT actions=conjunction($VM2_CONJ_ID,2/2)"

ovs-ofctl add-flow br0 -O openflow13 "priority=1 table=15 actions=set_field:0xf->reg8,goto_table:200"

ovs-ofctl add-flow br0 -O openflow13 "priority=50 table=20 actions=goto_table:45"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=45,dl_dst=$VM1_MAC actions=set_field:$VM1_PORT->reg7,goto_table:50"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=45,dl_dst=$VM2_MAC actions=set_field:$VM2_PORT->reg7,goto_table:50"

ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=50,ip actions=ct(table=55,zone=NXM_NX_REG7[0..15])"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=55,ct_state=-new+est-rel-inv+trk actions=goto_table:60"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=55,ct_state=-new+rel-inv+trk actions=goto_table:60"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=55,ct_state=+new+rel-inv+trk,ip actions=ct(commit,table=60,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=2000 table=55,ct_state=+inv+trk,ip actions=set_field:0x96->reg8,goto_table:200"

ovs-ofctl add-flow br0 -O openflow13 "priority=1000 table=55,conj_id=$VM1_REV_CONJ_ID,ip,reg7=$VM1_PORT actions=ct(commit,table=60,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=55,ct_state=+new-est-rel-inv+trk,reg7=$VM1_PORT actions=conjunction($VM1_REV_CONJ_ID,1/2)"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=55,ip,reg7=$VM1_PORT actions=conjunction($VM1_REV_CONJ_ID,2/2)"

ovs-ofctl add-flow br0 -O openflow13 "priority=1000 table=55,conj_id=$VM2_REV_CONJ_ID,ip,reg7=$VM2_PORT actions=ct(commit,table=60,zone=NXM_NX_CT_ZONE[])"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=55,ct_state=+new-est-rel-inv+trk,reg7=$VM2_PORT actions=conjunction($VM2_REV_CONJ_ID,1/2)"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=55,ip,reg7=$VM2_PORT actions=conjunction($VM2_REV_CONJ_ID,2/2)"

ovs-ofctl add-flow br0 -O openflow13 "priority=1 table=55 actions=set_field:55->reg8,goto_table:200"

ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=60,reg7=$VM1_PORT actions=output:$VM1_PORT"
ovs-ofctl add-flow br0 -O openflow13 "priority=100 table=60,reg7=$VM2_PORT actions=output:$VM2_PORT"


return


#############below is the data path#####

[root@localhost wangzhike]# ovs-appctl dpif/dump-flows br0
recirc_id(0x10),in_port(3),eth(),eth_type(0x0800),ipv4(frag=no), packets:1, bytes:74, used:5.467s, flags:S, actions:2
recirc_id(0xf),in_port(3),ct_state(+new-est-rel-inv+trk),eth(),eth_type(0x0800),ipv4(frag=no), packets:1, bytes:74, used:5.467s, flags:S, actions:ct(commit,zone=1),recirc(0x10)
recirc_id(0),in_port(2),eth(),eth_type(0x0800),ipv4(frag=no), packets:141681, bytes:9383794, used:0.000s, flags:SP., actions:ct(zone=1),recirc(0x11)
recirc_id(0x12),in_port(2),ct_state(-new+est-rel-inv+trk),eth(),eth_type(0x0800),ipv4(frag=no), packets:141681, bytes:9383794, used:0.000s, flags:SP., actions:3
recirc_id(0xd),in_port(3),ct_state(+new-est-rel-inv+trk),eth(),eth_type(0x0800),ipv4(frag=no), packets:1, bytes:74, used:5.467s, flags:S, actions:ct(commit,zone=2),recirc(0xe)
recirc_id(0xd),in_port(3),ct_state(-new+est-rel-inv+trk),eth(dst=5e:e6:1e:36:7a:59),eth_type(0x0800),ipv4(frag=no), packets:285503, bytes:14261457798, used:0.000s, flags:P., actions:ct(zone=1),recirc(0xf)
recirc_id(0x11),in_port(2),ct_state(-new+est-rel-inv+trk),eth(dst=46:df:c5:4a:40:f8),eth_type(0x0800),ipv4(frag=no), packets:141681, bytes:9383794, used:0.000s, flags:SP., actions:ct(zone=2),recirc(0x12)
recirc_id(0xe),in_port(3),eth(dst=5e:e6:1e:36:7a:59),eth_type(0x0800),ipv4(frag=no), packets:1, bytes:74, used:5.467s, flags:S, actions:ct(zone=1),recirc(0xf)
recirc_id(0xf),in_port(3),ct_state(-new+est-rel-inv+trk),eth(),eth_type(0x0800),ipv4(frag=no), packets:285506, bytes:14261653476, used:0.000s, flags:P., actions:2
recirc_id(0),in_port(3),eth(),eth_type(0x0800),ipv4(frag=no), packets:285509, bytes:14261718842, used:0.000s, flags:SP., actions:ct(zone=2),recirc(0xd)


