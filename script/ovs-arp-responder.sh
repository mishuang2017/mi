#!/bin/bash

set -x

br=br-vxlan

vf2=enp4s0f3
vf3=enp4s0f4

rep1=enp4s0f0_0
rep2=enp4s0f0_1
rep3=enp4s0f0_2

ovs-vsctl list-br | xargs -r -l ovs-vsctl del-br
service openvswitch restart
ovs-vsctl list-br | xargs -r -l ovs-vsctl del-br
sleep 2

ip netns exec n11 ifconfig $vf2 192.168.0.2/24 up
ip netns exec n11 ip route add 8.9.10.0/24 via 192.168.0.1 dev $vf2
ifconfig $rep2 0 up

ip netns exec n12 ifconfig $vf3 8.9.10.11/24 up
ifconfig $rep3 0 up

ovs-vsctl add-br $br
ovs-vsctl add-port $br $rep2 -- set Interface $rep2 ofport_request=2
ovs-vsctl add-port $br $rep3 -- set Interface $rep3 ofport_request=3
ovs-vsctl add-port $br $rep1 -- set Interface $rep1 ofport_request=4
ovs-vsctl -- --id=@p get port $rep1 -- --id=@m create mirror name=m0 select-all=true output-port=@p -- set bridge $br mirrors=@m

MAC2=02:25:d0:13:01:02
MAC3=02:25:d0:13:01:03

MAC=24:8a:07:ad:77:99

ovs-ofctl add-flow $br "table=0, in_port=2, dl_type=0x0806, nw_dst=192.168.0.1, actions=load:0x2->NXM_OF_ARP_OP[], move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[], mod_dl_src:${MAC}, move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[], move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[], load:0x248a07ad7799->NXM_NX_ARP_SHA[], load:0xc0a80001->NXM_OF_ARP_SPA[], in_port"
ovs-ofctl add-flow $br "table=0, in_port=2, dl_dst=${MAC}, ip, nw_src=192.168.0.2, nw_dst=8.9.10.11, actions=mod_dl_src=${MAC}, mod_dl_dst=${MAC3}, mod_nw_src=8.9.10.1, output:3"

ovs-ofctl add-flow $br "table=0, in_port=3, dl_type=0x0806, nw_dst=8.9.10.1, actions=load:0x2->NXM_OF_ARP_OP[], move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[], mod_dl_src:${MAC}, move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[], move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[], load:0x248a07ad7799->NXM_NX_ARP_SHA[], load:0x08090a01->NXM_OF_ARP_SPA[], in_port"
ovs-ofctl add-flow $br "table=0, in_port=3, dl_dst=${MAC}, dl_type=0x0800, nw_dst=8.9.10.1, actions=mod_dl_src=24:8a:07:ad:77:88 mod_dl_dst=${MAC2}, mod_nw_dst=192.168.0.2, output:2"

set +x
