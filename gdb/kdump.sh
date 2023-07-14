define tasks
        set $tasks_off=((size_t)&((struct task_struct *)0)->tasks)
        set $pid_off=((size_t)&((struct task_struct *)0)->thread_group.next)
        set $init_t=&init_task
        set $next_t=(((char *)($init_t->tasks).next) - $tasks_off)
        set var $stacksize = sizeof(union thread_union)
        while ($next_t != $init_t)
                set $next_t=(struct task_struct *)$next_t
                printf "\npid %d; comm %s, prio %d, static_prio: %d:\n", $next_t.pid, $next_t.comm, $next_t.prio, $next_t.static_prio
                printf "===================\n"
                set $next_th=(((char *)$next_t->thread_group.next) - $pid_off)
                while ($next_th != $next_t)
                        set $next_th=(struct task_struct *)$next_th
			printf "\npid %d; comm %s, prio %d, static_prio: %d:\n", $next_t.pid, $next_t.comm, $next_t.prio, $next_t.static_prio
                        printf "===================\n"
                        set $next_th=(((char *)$next_th->thread_group.next) - $pid_off)
                end
                set $next_t=(char *)($next_t->tasks.next) - $tasks_off
        end
end
