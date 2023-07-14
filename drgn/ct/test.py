#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
from lib import *

prog = drgn.program_from_kernel()
# prog['jiffies']
prog.type('unsigned long')
# prog['jiffies']
prog.variable('jiffies')
