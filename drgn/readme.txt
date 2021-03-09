import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

exec(open("/labhome/chrism/sm/drgn/net.py").read())
