#include <linux/init.h>
#include <linux/module.h>
#include <linux/sysfs.h>

MODULE_LICENSE("Dual BSD/GPL");

static int test2_init(void)
{
	int i = 0;

	for (i = 0; i < 100; i++)
		printk(KERN_ALERT "test2 enter, %d, %d\n", i, order_base_2(i));
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
