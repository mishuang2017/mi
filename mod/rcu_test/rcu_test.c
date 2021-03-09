#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>

struct foo {
	int a;
	char b;
	long c;
	struct rcu_head rcu;
};
DEFINE_SPINLOCK(foo_mutex);

struct foo __rcu *gbl_foo;

void foo_update_a(int new_a)
{
	struct foo *new_fp;
	struct foo *old_fp;

	new_fp = kmalloc(sizeof(*new_fp), GFP_KERNEL);
	spin_lock(&foo_mutex);
	old_fp = rcu_dereference_protected(gbl_foo, lockdep_is_held(&foo_mutex));
	*new_fp = *old_fp;
	new_fp->a = new_a;
	rcu_assign_pointer(gbl_foo, new_fp);
	spin_unlock(&foo_mutex);
	synchronize_rcu();
	kfree(old_fp);
}

int foo_get_a(void)
{
	int retval;

	rcu_read_lock();
	retval = rcu_dereference(gbl_foo)->a;
	rcu_read_unlock();
	return retval;
}

void foo_reclaim(struct rcu_head *rp)
{
	struct foo *fp = container_of(rp, struct foo, rcu);

	kfree(fp);
}

void foo_update_a2(int new_a)
{
	struct foo *new_fp;
	struct foo *old_fp;

	new_fp = kmalloc(sizeof(*new_fp), GFP_KERNEL);
	spin_lock(&foo_mutex);
	old_fp = rcu_dereference_protected(gbl_foo, lockdep_is_held(&foo_mutex));
	*new_fp = *old_fp;
	new_fp->a = new_a;
	rcu_assign_pointer(gbl_foo, new_fp);
	spin_unlock(&foo_mutex);
	call_rcu(&old_fp->rcu, foo_reclaim);
}

MODULE_LICENSE("Dual BSD/GPL");

static int rcu_test_init(void)
{
	int a = 0;

	gbl_foo = kmalloc(sizeof(struct foo), GFP_KERNEL);
	foo_update_a2(1);
	a = foo_get_a();
	printk(KERN_ALERT "rcu_test enter, %d\n", a);
	return 0;
}

static void rcu_test_exit(void)
{
	printk(KERN_ALERT "rcu_test exit\n");
}

module_init(rcu_test_init);
module_exit(rcu_test_exit);

MODULE_AUTHOR("mishuang");
MODULE_DESCRIPTION("A Sample Hello World Module");
MODULE_ALIAS("A Sample module");
