#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int PAGE_OFFSET_init(void)
{
	printk(KERN_ALERT "PAGE_OFFSET: %lx\n", PAGE_OFFSET);
	printk(KERN_ALERT "__START_KERNEL_map: %lx\n", __START_KERNEL_map);
	return 0;
}

static void PAGE_OFFSET_exit(void)
{
	printk(KERN_ALERT "PAGE_OFFSET exit\n");
}

module_init(PAGE_OFFSET_init);
module_exit(PAGE_OFFSET_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
