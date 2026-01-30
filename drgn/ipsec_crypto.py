#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
ipsec = mlx5e_priv.ipsec
print(ipsec)
# exit(0)
print(mlx5e_priv.netdev.xfrmdev_ops)

def print_sadb(sadb):
    for i in range(1024):
        node = sadb[i].first
        while node.value_():
            obj = container_of(node, "struct mlx5e_ipsec_sa_entry", "hlist")
            sa = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=obj.value_())
            print("sa->attrs->flags, MLX5_ACCEL_ESP_FLAGS_TUNNEL 1, MLX5_ACCEL_ESP_FLAGS_FULL_OFFLOAD 8\n")
            print(sa)
            print(sa.ipsec.aso)
            print(sa.ipsec.aso.maso)
            print(sa.ipsec.aso.umr)
            
            print_mlx5_flow_handle(sa.ipsec_rule.rule)

            node = node.next

sadb = ipsec.sadb
print("\n======================== tx ===========================\n")
# print(sadb)
flow_table("sa", ipsec.tx.ft.sa)
flow_table("pol", ipsec.tx.ft.pol)

for node in radix_tree_for_each(sadb.address_of_()):
#     print(node)
    entry = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=node[1].value_())
#     print(entry.ipsec.tx)
#     print_mlx5_flow_handle(entry.ipsec_rule.rule)

def print_net_xfrm_state(net):
    netns_xfrm = net.xfrm

    print("\n======================== net.xfrm.state ===========================\n")

    i=1
    for x in list_for_each_entry('struct xfrm_state', netns_xfrm.state_all.address_of_(), 'km.all'):
        print(" --- %d ---\n" % i)

        print(x.type_offload)
# *(const struct xfrm_type_offload *)0xffffffffc13cf0c0 = {
#         .owner = (struct module *)0xffffffffc13cd080,
#         .proto = (u8)50,
#         .encap = (void (*)(struct xfrm_state *, struct sk_buff *))esp4_gso_encap+0x0 = 0xffffffffc148f010,
#         .input_tail = (int (*)(struct xfrm_state *, struct sk_buff *))esp_input_tail+0x0 = 0xffffffffc148f0e0,
#         .xmit = (int (*)(struct xfrm_state *, struct sk_buff *, netdev_features_t))esp_xmit+0x0 = 0xffffffffc148fa90,
# }

# 3.411096 0       0       swapper/21      esp_input_tail
#         esp_input_tail+0x5 [esp4_offload]
#         esp4_gro_receive+0x239 [esp4_offload]
#         inet_gro_receive+0x2c9 [kernel]
#         dev_gro_receive+0x4ba [kernel]
#         gro_receive_skb+0xa5 [kernel]
#         mlx5e_rep_tc_receive+0x63 [mlx5_core]
#         mlx5e_handle_rx_cqe_mpwrq_rep+0x13f [mlx5_core]
#         mlx5e_rx_cq_process_basic_cqe_comp+0x3b3 [mlx5_core]
#         mlx5e_poll_rx_cq+0x50 [mlx5_core]
#         mlx5e_napi_poll+0x135 [mlx5_core]
#         __napi_poll.constprop.0+0x2f [kernel]
#         net_rx_action+0x316 [kernel]
#         handle_softirqs+0xd3 [kernel]
#         __irq_exit_rcu+0xf4 [kernel]
#         irq_exit_rcu+0x12 [kernel]
#         common_interrupt+0xb5 [kernel]
#         asm_common_interrupt+0x2b [kernel]
#         pv_native_safe_halt+0xf [kernel]
#         arch_cpu_idle+0xd [kernel]
#         default_idle_call+0x82 [kernel]
#         cpuidle_idle_call+0x14b [kernel]
#         do_idle+0x89 [kernel]
#         cpu_startup_entry+0x30 [kernel]
#         start_secondary+0x116 [kernel]
#         common_startup_64+0x13e [kernel]

# 9.892734 61847   61847   cc1             esp4_gso_encap
#         esp4_gso_encap+0x5 [esp4_offload]
#         xfrm_output_resume+0x56 [kernel]
#         xfrm_output+0x14d [kernel]
#         __xfrm4_output+0x3e [kernel]
#         xfrm4_output+0x4b [kernel]
#         ip_push_pending_frames+0x141 [kernel]
#         icmp_push_reply+0xd7 [kernel]
#         icmp_reply+0x404 [kernel]
#         icmp_echo.part.0+0x62 [kernel]
#         icmp_echo+0x4e [kernel]
#         icmp_rcv+0x258 [kernel]
#         ip_protocol_deliver_rcu+0x21d [kernel]
#         ip_local_deliver_finish+0xe2 [kernel]
#         ip_local_deliver+0x7b [kernel]
#         ip_sublist_rcv_finish+0xd5 [kernel]
#         ip_list_rcv_finish+0x1ae [kernel]
#         ip_list_rcv+0x150 [kernel]
#         __netif_receive_skb_list_core+0x27d [kernel]
#         netif_receive_skb_list_internal+0x1eb [kernel]
#         napi_complete_done+0x89 [kernel]
#         gro_cell_poll+0x199 [kernel]
#         __napi_poll.constprop.0+0x2f [kernel]
#         net_rx_action+0x316 [kernel]
#         handle_softirqs+0xd3 [kernel]
#         __irq_exit_rcu+0xf4 [kernel]
#         irq_exit_rcu+0x12 [kernel]
#         common_interrupt+0x57 [kernel]
#         asm_common_interrupt+0x2b [kernel]

# 6.228209 0       0       swapper/21      esp_xmit
#         esp_xmit+0x5 [esp4_offload]
#         validate_xmit_skb+0x234 [kernel]
#         validate_xmit_skb_list+0x51 [kernel]
#         sch_direct_xmit+0x1d2 [kernel]
#         __dev_xmit_skb+0x325 [kernel]
#         __dev_queue_xmit+0x442 [kernel]
#         neigh_hh_output+0x105 [kernel]
#         ip_finish_output2+0x24f [kernel]
#         __ip_finish_output+0x16a [kernel]
#         ip_finish_output+0x2e [kernel]
#         ip_output+0xa7 [kernel]
#         xfrm_output_resume+0x5f0 [kernel]
#         xfrm_output+0x14d [kernel]
#         __xfrm4_output+0x3e [kernel]
#         xfrm4_output+0x4b [kernel]
#         ip_push_pending_frames+0x141 [kernel]
#         icmp_push_reply+0xd7 [kernel]
#         icmp_reply+0x404 [kernel]
#         icmp_echo.part.0+0x62 [kernel]
#         icmp_echo+0x4e [kernel]
#         icmp_rcv+0x258 [kernel]
#         ip_protocol_deliver_rcu+0x21d [kernel]
#         ip_local_deliver_finish+0xe2 [kernel]
#         ip_local_deliver+0x7b [kernel]
#         ip_sublist_rcv_finish+0xd5 [kernel]
#         ip_list_rcv_finish+0x1ae [kernel]
#         ip_list_rcv+0x150 [kernel]
#         __netif_receive_skb_list_core+0x27d [kernel]
#         netif_receive_skb_list_internal+0x1eb [kernel]
#         napi_complete_done+0x89 [kernel]
#         gro_cell_poll+0x199 [kernel]
#         __napi_poll.constprop.0+0x2f [kernel]
#         net_rx_action+0x316 [kernel]
#         handle_softirqs+0xd3 [kernel]
#         __irq_exit_rcu+0xf4 [kernel]
#         irq_exit_rcu+0x12 [kernel]
#         common_interrupt+0xb5 [kernel]
#         asm_common_interrupt+0x2b [kernel]
#         pv_native_safe_halt+0xf [kernel]
#         arch_cpu_idle+0xd [kernel]
#         default_idle_call+0x82 [kernel]
#         cpuidle_idle_call+0x14b [kernel]
#         do_idle+0x89 [kernel]
#         cpu_startup_entry+0x30 [kernel]
#         start_secondary+0x116 [kernel]
#         common_startup_64+0x13e [kernel]

#         print(x.id)
#         print("x.xso.flags: XFRM_OFFLOAD_IPV6 1, XFRM_OFFLOAD_INBOUND 2, XFRM_OFFLOAD_FULL, 4")
#         print(x.xso)
        i+=1

def print_net_xfrm_policy(net):
    netns_xfrm = net.xfrm

    print("\n======================== net.xfrm.policy ===========================\n")

    i=1
    for x in list_for_each_entry('struct xfrm_policy_walk_entry', netns_xfrm.policy_all.address_of_(), 'all'):
        print(" --- %d ---\n" % i)
#         print(x)
        policy = container_of(x, "struct xfrm_policy", "walk")
        print(policy)
        i+=1

net = prog['init_net']
print_net_xfrm_state(net)
# print_net_xfrm_policy(net)

print(ipsec.rx_ipv4)

# print_sadb(sadb)

# sadb = ipsec.sadb_rx
print("\n======================== rx ===========================\n")
# print_sadb(sadb)

flow_table("rx_ipv4.ft.sa", ipsec.rx_ipv4.ft.sa)
flow_table("rx_ipv4.ft.status", ipsec.rx_ipv4.ft.status)
flow_table("rx_ipv4.ft_pol", ipsec.rx_ipv4.ft.pol)
flow_table("rx_ipv4.pol_miss_ft", ipsec.rx_ipv4.pol_miss_ft)
# print(ipsec.rx_ipv4)

exit(0)
# print(ipsec.aso)
# print(ipsec.aso.maso)

def print_counters():
    print("\n======================== counters ===========================\n")

    fc = ipsec_priv.decap_rule_counter
    print("decap_rule_counter       id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.decap_miss_rule_counter
    print("decap_miss_rule_counter  id: %x, packets: %d" % (fc.id, fc.cache.packets))

    fc = ipsec_priv.tx_chk_rule_counter
    print("tx_chk_rule_counter      id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.tx_chk_drop_rule_counter
    print("tx_chk_drop_rule_counter id: %x, packets: %d" % (fc.id, fc.cache.packets))

print_counters()


print("\n======================== ipsec_priv ===========================\n")
esw = mlx5e_priv.mdev.priv.eswitch
ipsec_priv = esw.fdb_table.offloads.esw_ipsec_priv
print(ipsec_priv)

print("\n======================== ipsec_fdb_crypto_rx, FDB_CRYPTO_INGRESS, level 1 ===========================\n")
flow_table("ipsec_fdb_crypto_rx", ipsec_priv.ipsec_fdb_crypto_rx)
print("\n======================== ipsec_fdb_decap_rx,  FDB_CRYPTO_INGRESS, level 2 ===========================\n")
flow_table("ipsec_fdb_decap_rx", ipsec_priv.ipsec_fdb_decap_rx)

print("\n======================== ipsec_fdb_ike_tx,    FDB_CRYPTO_EGRESS,  level 1 ===========================\n")
flow_table("ipsec_fdb_ike_tx", ipsec_priv.ipsec_fdb_ike_tx)
print("\n======================== ipsec_fdb_crypto_tx, FDB_CRYPTO_EGRESS,  level 2 ===========================\n")
flow_table("ipsec_fdb_crypto_tx", ipsec_priv.ipsec_fdb_crypto_tx)
print("\n======================== ipsec_fdb_tx_chk,    FDB_CRYPTO_EGRESS,  level 3 ===========================\n")
flow_table("ipsec_fdb_tx_chk", ipsec_priv.ipsec_fdb_tx_chk)

uar = mlx5e_priv.mdev.priv.uar
# print(uar)
