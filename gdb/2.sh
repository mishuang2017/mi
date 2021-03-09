# set max-value-size unlimited
set confirm off
set print pretty on

# source ~chrism/gdb/1.sh
# source ~chrism/gdb/2.sh
# alias 1 = source

set $print = 1
set $debug = 0

#
# arg0: name of data struct, string
# arg1: name of data struct, variable
# arg2: pointer of the buckets of the hmap
# arg3: how many elements
# arg4: hmap_node name in data struct
# arg5: member name to print in data struct, optional
#
define print-hmap
	set $name = $arg0
	set $p = $arg2
	set $num = $arg3
	set $index = 1

	set $i = 0
	while $i != $num
		set $a = *$p
		if $a != 0
			if $debug == 1
				printf "======= %d =======\n", $index
				set $index = $index + 1
			end
			if $print == 0
				printf "p *(struct %s *) 0x%x\n", $name, $a
			else
				if $argc == 6
					p/s (*(struct $arg1 *) $a).$arg5
				else
					p/s *(struct $arg1 *) $a
				end
			end
			set $i = $i + 1
			set $node = (*(struct $arg1 *) $a)->$arg4.next
			while $node != 0
				if $debug == 1
					printf "======= %d =======\n", $index
					set $index = $index + 1
				end
				if $print == 0
					printf "p *(struct %s *) 0x%x\n", $name, $node
				else
					if $argc == 6
						p/s (*(struct $arg1 *) $node).$arg5
					else
						p/s *(struct $arg1 *) $node
					end
				end
				set $node = (*(struct $arg1 *) $node)->$arg4.next
				set $i = $i + 1
			end
		end
		set $p = $p + $delta
	end
end

#
# arg0: name of data struct, string
# arg1: name of data struct, variable
# arg2: pointer of the buckets of the hmap
# arg3: how many elements
# arg4: member name to print in data struct, optional
#
define print-shash
	set $name = $arg0
	set $p = $arg2
	set $num = $arg3
	set $index = 1

	set $i = 0
	while $i != $num
		set $a = *$p
		if $a != 0
			if $debug == 1
				printf "======= %d =======\n", $index
				set $index = $index + 1
			end
			if $print == 0
				printf "p *(struct %s *) 0x%x\n", $name, $a
			else
				echo node-->
				p/x $a
				set $name = (*(struct shash_node *) $a).name
				p/s $name
				set $data = (*(struct shash_node *) $a).data
				p/s *(struct $arg1 *) $data
#                                 p/s *(struct netdev_vport *) $data
# 				p/x *(struct $arg1 *) $a
			end
			set $i = $i + 1
			set $a_next = (*(struct shash_node *) $a)->node.next
			while $a_next != 0
				if $debug == 1
					printf "======= %d =======\n", $index
					set $index = $index + 1
				end
				if $print == 0
					printf "p *(struct %s *) 0x%x\n", $name, $a_next
				else
					echo node-->
					p/x $a_next
					set $name = (*(struct shash_node *) $a_next).name
					p/s $name
					set $data = (*(struct shash_node *) $a_next).data
					p/s *(struct $arg1 *) $data
# 					p/s *(struct netdev_vport *) $data
# 					p/x *(struct shash_node *) $a_next
				end
				set $a_next = (*(struct shash_node *) $a_next)->node.next
				set $i = $i + 1
			end
		end
		set $p = $p + $delta
	end
end

define shash
	set $print = 1
	set $delta = 1
	set $p = (*(struct shash*)&netdev_shash)->map.buckets
	set $num = (*(struct shash*)&netdev_shash)->map.n
	p $p
	print-shash "shash_node" netdev $p $num
end

################################################################################

define print-ufids-tc
	set $delta = 1
	set $p = (*(struct hmap *)&ufid_tc)->buckets
	p $p
	set $num = (*(struct hmap *)&ufid_tc)->n
	p $num
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "ufid_tc_data" ufid_tc_data $p $num tc_node $arg1
	else
		print-hmap "ufid_tc_data" ufid_tc_data $p $num tc_node
	end
end
define ufid-tc
	print-ufids-tc 0
end
define ufid-tc2
	if $argc == 0
		print-ufids-tc 1
	else
		print-ufids-tc 1 $arg0
	end
end



################################################################################

define print-ufids
	set $delta = 1
	set $p = (*(struct hmap *)&ufid_tc)->buckets
	p $p
	set $num = (*(struct hmap *)&ufid_tc)->n
	p $num
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "ufid_tc_data" ufid_tc_data $p $num ufid_node $arg1
	else
		print-hmap "ufid_tc_data" ufid_tc_data $p $num ufid_node
	end
end
define ufid
	print-ufids 0
end
define ufid2
	if $argc == 0
		print-ufids 1
	else
		print-ufids 1 $arg0
	end
end

################################################################################

define print-xports
	set $delta = 1
        set $p = (*(struct xlate_cfg*) xcfgp)->xports.buckets
        set $num = (*(struct xlate_cfg*) xcfgp)->xports.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "xport" xport $p $num hmap_node $arg1
	else
		print-hmap "xport" xport $p $num hmap_node
	end
end
define xport
	print-xports 0
end
define xport2
	if $argc == 0
		print-xports 1
	else
		print-xports 1 $arg0
	end
end

################################################################################

define print-xbundles
	set $delta = 1
        set $p = (*(struct xlate_cfg*) xcfgp)->xbundles.buckets
        set $num = (*(struct xlate_cfg*) xcfgp)->xbundles.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "xbundle" xbundle $p $num hmap_node $arg1
	else
		print-hmap "xbundle" xbundle $p $num hmap_node
	end
end
define xbundle
	print-xbundles 0
end
define xbundle2
	if $argc == 0
		print-xbundles 1
	else
		print-xbundles 1 $arg0
	end
end

################################################################################

define print-xbridges
	set $delta = 1
        set $p = (*(struct xlate_cfg*) xcfgp)->xbridges.buckets
        set $num = (*(struct xlate_cfg*) xcfgp)->xbridges.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "xbridge" xbridge $p $num hmap_node $arg1
	else
		print-hmap "xbridge" xbridge $p $num hmap_node
	end
end
define xbridge
	print-xbridges 0
end
define xbridge2
	if $argc == 0
		print-xbridges 1
	else
		print-xbridges 1 $arg0
	end
end

################################################################################

# define print-all-ofproto-dpifs
# 	set $delta = 1
#         set $p = all_ofproto_dpifs.buckets
#         set $num = all_ofproto_dpifs.n
# 	if $arg0 == 0
# 		set $print = 0
# 		p/x $num
# 	else
# 		set $print = 1
# 	end
# 	if $argc == 2
# 		print-hmap "ofproto_dpif" ofproto_dpif $p $num all_ofproto_dpifs_node $arg1
# 	else
# 		print-hmap "ofproto_dpif" ofproto_dpif $p $num all_ofproto_dpifs_node
# 	end
# end
# define ofproto-dpif
# 	print-all-ofproto-dpifs 0
# end
# define ofproto-dpif2
# 	if $argc == 0
# 		print-all-ofproto-dpifs 1
# 	else
# 		print-all-ofproto-dpifs 1 $arg0
# 	end
# end

################################################################################
#
# ofproto_dpif->bundles
#
# (gdb) ofproto-dpif2 bundles
# ======= 1 =======
# $4 = {
#   buckets = 0x1245980,
#   one = 0x0,
#   mask = 3,
#   n = 4
# }
# (gdb) ofbundle 0x1245980 4

define print-ofbundles
	set $delta = 8
        set $p = $arg0
        set $num = $arg1
	if $arg2 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 4
		print-hmap "ofbundle" ofbundle $p $num hmap_node $arg3
	else
		print-hmap "ofbundle" ofbundle $p $num hmap_node 
	end
end
define ofbundle
	print-ofbundles $arg0 $arg1 0
end
define ofbundle2
	if $argc == 2
		print-ofbundles $arg0 $arg1 1
	else
		print-ofbundles $arg0 $arg1 1 $arg2
	end
end

################################################################################
# start point
################################################################################

define print-all-ofprotos
	set $delta = 1
        set $p = all_ofprotos.buckets
        set $num = all_ofprotos.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "ofproto" ofproto $p $num hmap_node $arg1
	else
		print-hmap "ofproto" ofproto $p $num hmap_node
	end
end
define ofproto
	print-all-ofprotos 0
end
define ofproto2
	if $argc == 0
		print-all-ofprotos 1
	else
		print-all-ofprotos 1 $arg0
	end
end

#
# call ofproto_dpif_cast to get
# struct ofproto_dpif
#

################################################################################
#
# (gdb) ofproto2 ports
# ======= 1 =======
# $7 = {
#   buckets = 0x122af80,
#   one = 0x0,
#   mask = 3,
#   n = 4
# }
# (gdb) ofport 0x122af80 4

define print-ofports
	set $delta = 8
        set $p = $arg0
        set $num = $arg1
	if $arg2 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 4
		print-hmap "ofport" ofport $p $num hmap_node $arg3
	else
		print-hmap "ofport" ofport $p $num hmap_node 
	end
end
define ofport
	print-ofports $arg0 $arg1 0
end
define ofport2
	if $argc == 2
		print-ofports $arg0 $arg1 1
	else
		print-ofports $arg0 $arg1 1 $arg2
	end
end

################################################################################

define print-port-to-netdevs
	set $delta = 1
	set $p = port_to_netdev.buckets
	set $num = port_to_netdev.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "port_to_netdev_data" port_to_netdev_data $p $num portno_node $arg1
	else
		print-hmap "port_to_netdev_data" port_to_netdev_data $p $num portno_node
	end
end
define port-to-netdev
	print-port-to-netdevs 0
end
define port-to-netdev2
	if $argc == 0
		print-port-to-netdevs 1
	else
		print-port-to-netdevs 1 $arg0
	end
end

################################################################################

define print-ifindex-to-ports
	set $delta = 1
	set $p = ifindex_to_port.buckets
	set $num = ifindex_to_port.n
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	if $argc == 2
		print-hmap "ifindex_to_port_data" ifindex_to_port_data $p $num node $arg1
	else
		print-hmap "ifindex_to_port_data" ifindex_to_port_data $p $num node
	end
end
define ifindex-to-port
	print-ifindex-to-ports 0
end
define ifindex-to-port2
	if $argc == 0
		print-ifindex-to-ports 1
	else
		print-ifindex-to-ports 1 $arg0
	end
end

################################################################################

define print-backer
	set $delta = 1
        set $shash_node = all_dpif_backers.map.one
        p/x $shash_node
	set $backer = (*(struct shash_node *) $shash_node)->data
        p/x $backer
        p *(struct dpif_backer *)$backer
end

define print-udpif
	set $delta = 1
        set $shash_node = all_dpif_backers.map.one
        p/x $shash_node
	set $backer = (*(struct shash_node *) $shash_node)->data
        p/x $backer
        p *((struct dpif_backer *)$backer).udpif
end

# print all_udpifs
# print *(struct udpif *) all_udpifs.next

# (gdb) p *((struct handler *) 0x2097740)@11

define print-handlers
	set $delta = 1
	set $shash_node = all_dpif_backers.map.one
	p/x $shash_node
	set $backer = (*(struct shash_node *) $shash_node)->data
	p/x $backer
	set $n = (*((struct dpif_backer *)$backer).udpif).n_handlers
	p/x *(*((struct dpif_backer *)$backer).udpif).handlers@$n
end


define print-ofport-dpifs
	if $arg0 == 0
		set $print = 0
		p/x $num
	else
		set $print = 1
	end
	set $shash_node = all_dpif_backers.map.one
	p/x $shash_node
	set $backer = (*(struct shash_node *) $shash_node)->data
	p/x $backer
	p (*(struct dpif_backer *)$backer).odp_to_ofport_map
	set $p = (*(struct dpif_backer *)$backer).odp_to_ofport_map.buckets
	set $num = (*(struct dpif_backer *)$backer).odp_to_ofport_map.n
	if $argc == 2
		print-hmap "ofport_dpif" ofport_dpif $p $num odp_port_node $arg1
	else
		print-hmap "ofport_dpif" ofport_dpif $p $num odp_port_node
	end
end
define ofport-dpif
	print-ofport-dpifs 0
end
define ofport-dpif2
	if $argc == 0
		print-ofport-dpifs 1
	else
		print-ofport-dpifs 1 $arg0
	end
end

################################################################################

define print-mbridge
	set $mbridge = (*(struct xbridge *) $arg0).mbridge
	p/x $mbridge
	p (*(struct mbridge *) $mbridge )

	set $mirror = (*(struct xbridge *) $arg0).mbridge.mirrors[0]
	p/x $mirror
	if $mirror != 0
		p (*(struct mirror *) $mirror )

		set $out = (*(struct xbridge *) $arg0).mbridge.mirrors[0].out
		p/x $out
		p (*(struct mbundle *) $out )

		set $bundle = (*(struct xbridge *) $arg0).mbridge.mirrors[0].out.ofbundle
		p/x $bundle
		p (*(struct ofbundle *) $bundle )
	fi
end

################################################################################

# (gdb) xbridge2
# $8 = {
#   hmap_node = {
#     hash = 10955958,
#     next = 0x0
#   },
#   ofproto = 0x13af4e0,
#   xbundles = {
#     prev = 0x1405858,
#     next = 0x13ae3a8
#   },
# (gdb) ls-xbundle 0x13ae3a8 name
# $9 = 0x14064b0 "enp4s0f0_0"
# $10 = 0x1405840
# $11 = 0x13d7790 "br"
# $12 = 0x13ae390
#
define ls-xbundle
	set $offset = (int)&((struct xbundle*)0)->list_node
	if $argc == 1
		ls xbundle $offset $arg0
	end
	if $argc == 2
		ls xbundle $offset $arg0 $arg1
	end
end

define ls
	if $argc < 3
		echo ls "struct name" "offset" "list head address"\n
	else
		set $offset = $arg1
		set $head = $arg2
		set $node = $arg2
		set $i = 1
		while $i != 0
			if $node == $head
				set $node = *$node
			end
			if $argc == 3
				p (*(struct $arg0 *) (($node = *$node) - $offset))
			else
				p (*(struct $arg0 *) (($node = *$node) - $offset)).$arg3
			end
			p/x $node - $offset
			if $node == $head
				set $i = 0
			end
		end
	end
end

# print-xbundle $g_xbundles_head name

define print-netdev
	set $p = port_to_netdev.buckets
	p/x $p
	set $num = port_to_netdev.n
	p/x $num

	set $i = 0
	while $i != $num
		set $a = *$p
		p/x $a
		if $a != 0
			set $i = $i + 1
			p/x $i
			echo node-->
			set $dev = (*(struct port_to_netdev_data *) $a).netdev
			p/x $dev
			p *(struct netdev *) $dev
			set $node = (*(struct port_to_netdev_data *) $a)->portno_node.next
			while $node != 0
				set $i = $i + 1
				p/x $i
				set $dev = (*(struct port_to_netdev_data *) $node).netdev
				echo node-->
				p/x $dev
				p *(struct netdev *) $dev
				set $node = (*(struct port_to_netdev_data *) $node)->portno_node.next
			end
		end
		set $p = $p + 0x1
		p/x $p
	end
end

define print-netdev-vport
	set $p = port_to_netdev.buckets
	p/x $p
	set $num = port_to_netdev.n
	p/x $num

	set $i = 0
	while $i != $num
		set $a = *$p
		p/x $a
		if $a != 0
			set $i = $i + 1
			p/x $i
			echo node-->
			set $dev = (*(struct port_to_netdev_data *) $a).netdev
			p/x $dev
			p *(struct netdev_vport *) $dev
			set $node = (*(struct port_to_netdev_data *) $a)->portno_node.next
			while $node != 0
				set $i = $i + 1
				p/x $i
				set $dev = (*(struct port_to_netdev_data *) $node).netdev
				echo node-->
				p/x $dev
				p *(struct netdev_vport *) $dev
				set $node = (*(struct port_to_netdev_data *) $node)->portno_node.next
			end
		end
		set $p = $p + 0x1
		p/x $p
	end
end

# set $dpif = all_ofproto_dpifs.one

define print-dpif
	p/x $dpif
	p/x *(struct ofproto_dpif *)$dpif
# 	p/x (*(struct ofproto_dpif *)$dpif)->netflow
end

set $ofproto = all_ofprotos.one

define print-ofproto
	echo struct ofproto\t
# 	p $ofproto
# 	p *(struct ofproto*)$ofproto

	set $tables = (*(struct ofproto*)$ofproto).tables
# 	echo struct oftable\t
# 	p $tables
# 	p/x *(struct oftable*) $tables

	set $cls = (*(struct ofproto*)$ofproto).tables->cls
# 	echo struct classifier\t
# 	p/s $cls
# 	p/x *(struct classifier*) $cls

	set $subtables = (*(struct ofproto*)$ofproto).tables->cls.subtables.impl.p
# 	echo struct subtable\t
# 	p $subtables
# 	p/x *(struct pvector_impl*) $subtables

	set $size = (*(struct pvector_impl*) $subtables).size
	p/x $size
	set $vector = (*(struct pvector_impl*) $subtables).vector
	p/x $vector

	set $i = 0
	while $i != $size
		set $i = $i + 1
		p/x *(struct pvector_entry*) $vector
		set $cls_subtable = (*(struct pvector_entry*) $vector).ptr
# 		echo struct cls_subtable\t
# 		p/x $cls_subtable
# 		p/x *(struct cls_subtable*) $cls_subtable

		set $rules = (*(struct cls_subtable*)$cls_subtable).rules.impl.p
		p/x $rules

		x (*(struct cls_subtable*)$cls_subtable).rules_list.prev
		set $rules_list = $_
		echo cls_rule\t
		p/x $rules_list
		p/x *(struct cls_rule*) $rules_list
		set $o = &((struct rule*)0)->cr
		# 8 bytes
		set $rule_dpif = $rules_list - 2
		echo rule_dpif\t
		p/x $rule_dpif
		p/x *(struct rule_dpif*) $rule_dpif

		set $rule_actions = (*(struct rule_dpif*) $rule_dpif)->up.actions
		echo rule_actions\t
		p/x $rule_actions
		p/x *(struct rule_actions*)$rule_actions

		set $ofpacts = (*(struct rule_actions*)$rule_actions)->ofpacts
		echo ofpacts\t
		p/x $ofpacts
		p/x *(struct ofpact_output*)$ofpacts

		set $miniflow = (*(struct cls_rule*)$rules_list)->match.flow
		x/50 $miniflow

		set $cls_match = (*(struct cls_rule*)$rules_list)->cls_match.p
		echo cls_match\t
		p/x $i
		p/x $cls_match
		p/x *(struct cls_match*) $cls_match

# 		echo cmap_impl\n
# 		p/x *(struct cmap_impl*) $rules

		set $vector = $vector + 1
# 		p/x $vector
	end

# 	p/x (*(struct ofproto_dpif *)$dpif)->netflow
end
