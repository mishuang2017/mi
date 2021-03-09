#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int test2_init(void)
{
	printk(KERN_ALERT "test2 enter, %d\n", HZ);
	return 0;
}

static void test2_exit(void)
{
	printk(KERN_ALERT "test2 exit\n");
}

module_init(test2_init);
module_exit(test2_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
