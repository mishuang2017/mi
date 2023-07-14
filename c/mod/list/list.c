#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

struct node {
	struct list_head list;
	int v;
};

struct list_head head;

static void test_list(void)
{
	struct node a;
	struct node b;
	struct node *n;

	INIT_LIST_HEAD(&head);

	a.v = 1;
	list_add(&a.list, &head);
	b.v = 2;
	list_add_tail(&b.list, &head);

	list_for_each_entry(n, &head, list) {
		pr_info("%d\n", n->v);
	}
}

static int list_init(void)
{
	pr_info("list enter\n");
	test_list();
	return 0;
}

static void list_exit(void)
{
	pr_info("list exit\n");
}

module_init(list_init);
module_exit(list_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
