#include <linux/init.h>
#include <linux/slab.h>
#include <linux/module.h>
#include <linux/rhashtable.h>

MODULE_LICENSE("Dual BSD/GPL");

struct mlx5e_tc_flow {
	struct rhash_head	node;
	u64			cookie;
};

static const struct rhashtable_params tc_ht_params = {
	.head_offset = offsetof(struct mlx5e_tc_flow, node),
	.key_offset = offsetof(struct mlx5e_tc_flow, cookie),
	.key_len = sizeof(((struct mlx5e_tc_flow *)0)->cookie),
	.automatic_shrinking = true,
};

struct rhashtable tc_ht;
struct mlx5e_tc_flow *flow1;
struct mlx5e_tc_flow *flow2;

static int hash_init(void)
{
	struct mlx5e_tc_flow *flow;
	struct mlx5e_tc_flow flow_p;

	flow1 = kmalloc(sizeof(*flow1), GFP_KERNEL);
	flow2 = kmalloc(sizeof(*flow2), GFP_KERNEL);

	pr_info("hash enter\n");
	rhashtable_init(&tc_ht, &tc_ht_params);

	flow1->cookie = 1;
	rhashtable_insert_fast(&tc_ht, &flow1->node, tc_ht_params);
	pr_info("%px\n", flow1);

	flow2->cookie = 1;
	rhashtable_insert_fast(&tc_ht, &flow2->node, tc_ht_params);
	pr_info("%px\n", flow2);

/* 	flow_p.cookie = 1; */
/* 	flow = rhashtable_lookup_fast(&tc_ht, &flow_p.cookie, tc_ht_params); */
/* 	pr_info("%px\n", flow); */

	return 0;
}

static void hash_exit(void)
{
	kfree(flow1);
	kfree(flow2);
	pr_info("hash exit\n");
}

module_init(hash_init);
module_exit(hash_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
