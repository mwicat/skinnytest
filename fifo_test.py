import time

from sccptest.sccptest import *

def test(*clients):
    print 'registered'
    time.sleep(999999)

firstSep = int('000000000000', 16)
lastSep = firstSep + 300



test.configs = [
    # dict(device='SEP%012X' % sep, serverAddress=('127.0.0.1', 2000), bindAddress=('127.0.0.%d' % i, 0)) for i, sep in enumerate(range(firstSep, lastSep+1))
    dict(device='SEP%012X' % sep, serverAddress=('10.5.0.186', 2000)) for i, sep in enumerate(range(firstSep, lastSep+1))
    ]

print test.configs
# print test.configs
test.client = True
