from utils import db
from get_functions import get_cpu, get_mem, get_disk, get_swap, get_processes
from add_functions import add_cpu, add_mem, add_disk, add_swap, add_proc
from datetime import datetime


def monitoring(info):
    ssh = db.session.ssh
    dt = datetime.now()
    cpu = get_cpu(ssh)
    disk_header, disk = get_disk(ssh)
    mem = get_mem(ssh)
    swap = get_swap(ssh)
    proc = get_processes(ssh, dt)
    proc2 = [p for p in proc if float(p['%CPU']) > 0 or float(p["%MEM"]) > 10]
    proc = [p for p in proc if float(p['%CPU']) > 0 or float(p["%MEM"]) > 0]
    add_disk(disk, dt, mac=db.session.mac)
    add_mem(mem, dt, mac=db.session.mac)
    add_swap(swap, dt, mac=db.session.mac)
    add_cpu(cpu, dt, mac=db.session.mac)
    add_proc(proc2, dt, mac=db.session.mac)

    if info == "cpu":
        return cpu
    elif info == "mem":
        return mem
    elif info == "swap":
        return swap
    elif info == "disk":
        return disk_header, disk, dt
    elif info == "proc":
        return proc
