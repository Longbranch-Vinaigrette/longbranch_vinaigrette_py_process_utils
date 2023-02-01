import os

import psutil


def get_processes_by_cwd(cwd: str) -> list:
    """Get process by cwd

    Returns a list of found processes information"""
    python_processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
        pcwd: str = proc.info["cwd"]
        if pcwd == cwd:
            python_processes.append(proc.info)
    return python_processes


def get_processes_and_subprocesses_by_cwd(cwd: str) -> list:
    """Get process and subprocesses by cwd

    Returns a list of found processes information"""
    # First we retrieve the masters
    python_processes: list = get_processes_by_cwd(cwd)

    # Now we retrieve the juniors)?
    child_processes: list = []
    for proc in psutil.process_iter(["pid", "ppid", "name", "cmdline", "cwd"]):
        # Parent pid
        ppid: str = proc.info["ppid"]
        for master_proc in python_processes:
            # Check if the master process pid is the same as this process ppid
            if master_proc["pid"] == ppid:
                # It's the master process
                child_processes.append(proc.info)
                break
    return python_processes


def kill_all_by_cwd(cwd: str, signal: int = 15):
    """Kill every process that matches the cwd and also kill subprocesses of that process"""
    processes = get_processes_and_subprocesses_by_cwd(cwd)
    for p in processes:
        pid = p["pid"]
        # https://unix.stackexchange.com/questions/317492/list-of-kill-signals
        # 9 Hard kill
        # 15 is SIGTERM (soft kill)
        # Doesn't kill things like terminal tabs, which is usually expected
        # also some programs might run some code before getting killed, which
        # is expected behaviour.

        # Kill
        os.kill(pid, signal)
