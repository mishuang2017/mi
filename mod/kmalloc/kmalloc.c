#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>

MODULE_LICENSE("Dual BSD/GPL");

void * a = NULL;
static int kmalloc_init(void)
{
	a = kmalloc(4*1024*1024, GFP_KERNEL);
	if (a == NULL)
		pr_err("kmalloc failed\n");
	pr_info("kmalloc enter\n");
	return 0;
}

static void kmalloc_exit(void)
{
	if (a == NULL)
		kfree(a);
	pr_info("kmalloc exit\n");
}

module_init(kmalloc_init);
module_exit(kmalloc_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
