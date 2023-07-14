import gdb
 
class Netdev(gdb.Command):
 
    def __init__(self):
        super(self.__class__, self).__init__("netdev", gdb.COMMAND_USER)
    def invoke(self, args, from_tty):
        s = gdb.execute('port-to-netdev2 netdev', to_string=True)
        b = s.split()
        i = 0
        for e in b:
            i = i + 1
            if i % 3 == 0:
                gdb.execute('print *(struct netdev *) ' + e)
Netdev()


class Test(gdb.Command):
 
    def __init__(self):
        super(self.__class__, self).__init__("test", gdb.COMMAND_USER)
    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        print len(argv)
        print argv
Test()
