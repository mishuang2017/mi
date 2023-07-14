import sys
from drgn.helpers.linux import find_task

pid = int(sys.argv[1])
uid = find_task(prog, pid).cred.uid.val.value_()
print(f'PID {pid} is being run by UID {uid}')
