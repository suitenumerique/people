import subprocess
import sys


def run_command(cmd, msg=None, shell=False, cwd='.', stdout=None):
    if msg is None:
        msg = f"# Running: {cmd}"
    if stdout is not None:
        stdout.write(msg + '\n')
        if stdout != sys.stdout:
            sys.stdout(msg)
    subprocess.check_call(cmd, shell=shell, cwd=cwd, stdout=stdout, stderr=stdout)
    if stdout is not None:
        stdout.flush()
