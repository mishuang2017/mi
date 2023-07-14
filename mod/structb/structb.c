#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

struct test_a
{
	int a;
	long b;
};

static int structb_init(void)
{
	struct test_a a;
	pr_info("structb enter\n");
	return 0;
}

static void structb_exit(void)
{
	pr_info("structb exit\n");
}

module_init(structb_init);
module_exit(structb_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
