#include <linux/init.h>
#include <linux/module.h>
#include <linux/rcu_node_tree.h>

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
{
	atomic_t a;
	printk(KERN_ALERT "hello: %lx\n", sizeof(a));

/* 	printk(KERN_ALERT "hello: NUM_RCU_NODES, %d\n", NUM_RCU_NODES); */
/* 	printk(KERN_ALERT "hello: NUM_RCU_LVL_0, %d\n", NUM_RCU_LVL_0); */
/* 	printk(KERN_ALERT "hello: NUM_RCU_LVL_2, %d\n", NUM_RCU_LVL_1); */
/* 	printk(KERN_ALERT "hello: NR_CPUS, %d\n", NR_CPUS); */
/* 	printk(KERN_ALERT "hello: RCU_FANOUT_1, %d\n", RCU_FANOUT_1); */
/* 	printk(KERN_ALERT "hello: RCU_FANOUT_2, %d\n", RCU_FANOUT_2); */
/* 	printk(KERN_ALERT "hello: RCU_FANOUT_3, %d\n", RCU_FANOUT_3); */
/* 	printk(KERN_ALERT "hello: RCU_FANOUT_4, %d\n", RCU_FANOUT_4); */
	return 0;
}

static void hello_exit(void)
{
	printk(KERN_ALERT "Hello World exit\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
