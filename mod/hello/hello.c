#include <linux/init.h>
#include <linux/module.h>
#include <linux/rcu_node_tree.h>
#include <net/flow_offload.h>

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
{
	printk(KERN_ALERT "%ld\n", 86400 * HZ + jiffies);
	printk(KERN_ALERT "2 %ld\n", jiffies);

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
