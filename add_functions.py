from models import *
from utils import db


def add_cpu(cpu, date, mac):
    dt = date
    us = cpu["us"]
    sy = cpu["sy"]
    ni = cpu["ni"]
    id = cpu["id"]
    wa = cpu["wa"]
    hi = cpu["hi"]
    si = cpu["si"]
    st = cpu["st"]
    cpu_obj = Cpu(dt=dt, us=us, sy=sy, ni=ni, id=id, wa=wa, hi=hi, si=si, st=st, mac=mac)
    db.session.add(cpu_obj)
    db.session.commit()


def add_mem(mem, date, mac):
    dt = date
    total = mem["total"]
    free = mem["free"]
    used = mem["used"]
    cache = mem["cache"]
    mem_obj = Mem(dt=dt, total=total, free=free, used=used, cache=cache, mac=mac)
    db.session.add(mem_obj)
    db.session.commit()


def add_swap(swap, date, mac):
    dt = date
    total = swap["total"]
    free = swap["free"]
    used = swap["used"]
    available = swap["avail"]
    swap_obj = Swap(dt=dt, total=total, free=free, used=used, available=available, mac=mac)
    db.session.add(swap_obj)
    db.session.commit()


def add_proc(proc, date, mac):
    for p in proc:
        dt = date
        pid = p["PID"]
        user = p["USER"]
        cpu = p["%CPU"]
        mem = p["%MEM"]
        state = p["S"]
        command = p["COMMAND"]
        p_obj = Process(dt=dt, pid=pid, user=user, cpu=cpu, mem=mem, state=state, command=command, mac=mac)
        db.session.add(p_obj)
        db.session.commit()


def add_disk(disks, date, mac):
    dt = date
    for disk in disks:
        Filesystem = disk['Filesystem']
        Size = disk['Size']
        Used = disk["Used"]
        Avail = disk["Avail"]
        Use = disk["Use"]
        Mounted_on = disk["Mounted_on"]
        disk_obj = Disk(dt=dt, Filesystem=Filesystem, Size=Size, Use=Use, Used=Used, Avail=Avail, Mounted_on=Mounted_on,
                        mac=mac)
        db.session.add(disk_obj)
    db.session.commit()
