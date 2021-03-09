#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

struct test_a
{
	int a;
};

static int structa_init(void)
{
	struct test_a a;

	pr_info("structa enter\n");
	return 0;
}

static void structa_exit(void)
{
	pr_info("structa exit\n");
}

module_init(structa_init);
module_exit(structa_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
