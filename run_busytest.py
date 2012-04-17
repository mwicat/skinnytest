import time
from subprocess import Popen
import sys


RETRIES = 3
WAIT = 1


def wait_then_kill(proc):
    finished = False
    cnt = 0
    while cnt < RETRIES and not finished:
        finished = proc.poll()
        cnt += 1
        time.sleep(1)
    if not finished:
        try:
            proc.kill()
        except OSError:
            pass


def check_proc(proc):
    proc.wait()
    proc_ok = proc.returncode == 0
    return proc_ok


recv_proc = Popen(["./sccptest.py", "busytest.py"])
time.sleep(2)

p1 = Popen(["./originate_skinny", "1102"])
p2 = Popen(["./originate_skinny", "1102"])

p1_ok = check_proc(p1)
p2_ok = check_proc(p2)
recv_ok = check_proc(recv_proc)

test_ok = recv_ok and (p1_ok != p2_ok)

print p1_ok, p2_ok, recv_ok
print test_ok

sys.exit(0 if test_ok else 1)
