#include <linux/init.h>
#include <linux/module.h>
#include <linux/rcu_node_tree.h>
#include <net/ip6_fib.h>

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
{
	struct fib6_entry_notifier_info info;
	struct fib6_info rt;

	info.rt = &rt;
	info.rt->fib6_dst.plen = 0;

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
