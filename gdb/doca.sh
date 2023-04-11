# source ~cmi/mi/gdb/doca.sh

define print_dev
# 	print *rte_eth_devices@2
	set $i = 0
	while $i < 2
		set $rte_eth_device = rte_eth_devices[$i]
		printf "\n=== rte_eth_devices[%d] ===\n", $i
# 		print $rte_eth_device
		set $data = $rte_eth_device.data
		printf "\n=== rte_eth_dev_data ===\n"
# 		print *((struct rte_eth_dev_data *) $data)
# 		print $data.owner
# 		set $j = 0
# 		while $j < $data.nb_rx_queues
# 			printf "\n=== rx_queues[%d] ===\n", $j
# 			set $rx_queue = $data->rx_queues[$j]
# 			print (*((struct mlx5_rxq_ctrl *) $rx_queue)).rxq.wqes
# 			set $mlx5_rxq_ctrl = (struct mlx5_rxq_ctrl *) $rx_queue
# 			print *$mlx5_rxq_ctrl
# 			set $j = $j + 1
# 		end
		set $dev_private = $data.dev_private
		printf "\n=== mlx5_priv ===\n"

		set $mlx5_priv = (struct mlx5_priv *) $dev_private
# 		print *$mlx5_priv
		set $txqs_n = $mlx5_priv->txqs_n
		print $txqs_n
		set $mlx5_txq_data = *$mlx5_priv->txqs
		print (*$mlx5_txq_data[0]).elts_head
		print (*$mlx5_txq_data[0]).elts_tail
		print (*$mlx5_txq_data[1]).elts_head
		print (*$mlx5_txq_data[1]).elts_tail

		set $i = $i + 1
	end
