#include <linux/init.h>
#include <linux/module.h>
#include <linux/idr.h>

MODULE_LICENSE("Dual BSD/GPL");

int start = 1;
int end = 10;
struct idr idr1;
struct idr idr2;

static int idr1_init(void)
{
	int ret;
	int i;

	idr_init(&idr1);
	idr_init(&idr2);
	for (i = 1; i <= 5; i ++) {
		ret = idr_alloc_cyclic(&idr1, NULL,
				       start, end + 1, GFP_KERNEL);
		printk(KERN_ALERT "ret = %d\n", ret);
	}
	idr_remove(&idr1, 3);
/* 	idr_set_cursor(&idr1, 1); */
	ret = idr_alloc_cyclic(&idr1, NULL,
			       start, end, GFP_KERNEL);
	printk(KERN_ALERT "ret = %d\n", ret);

	for (i = 1; i <= 5; i ++) {
		ret = idr_alloc_cyclic(&idr1, NULL,
				       start, end + 1, GFP_KERNEL);
		printk(KERN_ALERT "ret = %d\n", ret);
	}

	ret = idr_alloc(&idr1, NULL, 0, 1, GFP_KERNEL);
	printk(KERN_ALERT "ret: %d\n", ret);

	return 0;
}

static void idr1_exit(void)
{
	int i;
	for (i = 0; i <= 10; i ++) {
		idr_remove(&idr1, i);
	}
	printk(KERN_ALERT "idr1 exit\n");
	idr_destroy(&idr1);
}

module_init(idr1_init);
module_exit(idr1_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
