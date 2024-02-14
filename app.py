from flask import Flask, jsonify, render_template, request, redirect
import paramiko
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Disk(db.Model):
    num = db.Column(db.Integer, nullable=False, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False)
    Filesystem = db.Column(db.String(50), nullable=False)
    Size = db.Column(db.String(10), nullable=False)
    Used = db.Column(db.String(10), nullable=False)
    Avail = db.Column(db.String(10), nullable=False)
    Use = db.Column(db.String(10), nullable=False)
    Mounted_on = db.Column(db.String(50), nullable=False)


class Cpu(db.Model):
    dt = db.Column(db.DateTime, nullable=False, primary_key=True)
    us = db.Column(db.Float, nullable=False)
    sy = db.Column(db.Float, nullable=False)
    ni = db.Column(db.Float, nullable=False)
    id = db.Column(db.Float, nullable=False)
    wa = db.Column(db.Float, nullable=False)
    hi = db.Column(db.Float, nullable=False)
    si = db.Column(db.Float, nullable=False)
    st = db.Column(db.Float, nullable=False)


class Mem(db.Model):
    dt = db.Column(db.DateTime, nullable=False, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    cache = db.Column(db.Float, nullable=False)


class Swap(db.Model):
    dt = db.Column(db.DateTime, nullable=False, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    available = db.Column(db.Float, nullable=False)


class Process(db.Model):
    num = db.Column(db.Integer, nullable=False, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    cpu = db.Column(db.Float, nullable=False)
    mem = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(5), nullable=False)
    command = db.Column(db.String(50), nullable=False)


def get_cpu(ssh):
    stdin, stdout, stderr = ssh.exec_command('top -b -n 1 | grep Cpu')
    data = stdout.read().decode().strip().split()

    cpu = {
        "us": float(data[1]),
        "sy": float(data[3]),
        "ni": float(data[5]),
        "id": float(data[7]),
        "wa": float(data[9]),
        "hi": float(data[11]),
        "si": float(data[13]),
        "st": float(data[15])
        }
    return cpu


def get_mem(ssh):
    stdin, stdout, stderr = ssh.exec_command('top -n 1 -b | grep  "MiB Mem"')
    data = stdout.read().decode().strip().split()
    mem = {
        "total": float(data[3]),
        "free": float(data[5]),
        "used": float(data[7]),
        "cache": float(data[9])
        }
    return mem


def get_swap(ssh):
    stdin, stdout, stderr = ssh.exec_command('top -n 1 -b | grep  "MiB Swap"')
    data = stdout.read().decode().strip().split()
    swap = {
        "total": float(data[2]),
        "free": float(data[4]),
        "used": float(data[6]),
        "avail": float(data[8])
        }
    return swap


def get_disk(ssh):
    stdin, stdout, stderr = ssh.exec_command('df -h')
    data = stdout.read().decode().strip().split('\n')
    for i in range(len(data)):
        data[i] = data[i].split()
    disk_headers = data[0]
    disk_data = []
    for d in data[1:]:
        d_dict = {
            'Filesystem': d[0],
            'Size': d[1],
            'Used': d[2],
            'Avail': d[3],
            'Use':d[4],
            'Mounted_on': d[5]
        }
        disk_data.append(d_dict)
    return disk_headers, disk_data


def get_processes(ssh):
    stdin, stdout, stderr = ssh.exec_command("top -n1 -b | grep -E '^\s*[0-9]+|^\s*%CPU'")
    top_data = stdout.read().decode().strip()
    top_data = top_data.split('\n')
    for i in range(len(top_data)):
        top_data[i] = top_data[i].split()
    proc = []
    for p in top_data:
        #p = list(str(p).strip())
        d = {
            'PID': p[0],
            'USER': p[1],
            'S': p[7],
            '%CPU': p[8],
            '%MEM': p[9],
            'COMMAND': p[11]
        }
        proc.append(d)
    return proc


def add_cpu(cpu, date):
    dt = date
    us = cpu["us"]
    sy = cpu["sy"]
    ni = cpu["ni"]
    id = cpu["id"]
    wa = cpu["wa"]
    hi = cpu["hi"]
    si = cpu["si"]
    st = cpu["st"]
    cpu_obj = Cpu(dt=dt, us=us, sy=sy, ni=ni, id=id, wa=wa, hi=hi, si=si, st=st)
    db.session.add(cpu_obj)
    db.session.commit()


def add_mem(mem, date):
    dt = date
    total = mem["total"]
    free = mem["free"]
    used = mem["used"]
    cache = mem["cache"]
    mem_obj = Mem(dt=dt, total=total, free=free, used=used, cache=cache)
    db.session.add(mem_obj)
    db.session.commit()


def add_swap(swap, date):
    dt = date
    total = swap["total"]
    free = swap["free"]
    used = swap["used"]
    available = swap["avail"]
    swap_obj = Swap(dt=dt, total=total, free=free, used=used, available=available)
    db.session.add(swap_obj)
    db.session.commit()


def add_proc(proc, date):
    for p in proc:
        dt = date
        pid = p["PID"]
        user = p["USER"]
        cpu = p["%CPU"]
        mem = p["%MEM"]
        state = p["S"]
        command = p["COMMAND"]
        p_obj = Process(dt=dt, pid=pid, user=user, cpu=cpu, mem=mem, state=state, command=command)
        db.session.add(p_obj)
        db.session.commit()


def add_disk(disks, date):
    dt = date
    for disk in disks:
        Filesystem = disk['Filesystem']
        Size = disk['Size']
        Used = disk["Used"]
        Avail = disk["Avail"]
        Use = disk["Use"]
        Mounted_on = disk["Mounted_on"]
        disk_obj = Disk(dt=dt, Filesystem=Filesystem, Size=Size, Use=Use, Used=Used, Avail=Avail, Mounted_on=Mounted_on)
        db.session.add(disk_obj)
    db.session.commit()


@app.route('/cpu')
def show_cpu():
    dt, cpu, mem, swap, proc, disk_header, disk = monitoring()
    all_cpu = Cpu.query.order_by(Cpu.dt.desc()).limit(20).all()
    return render_template('cpu.html', cpu=cpu, all_cpu=all_cpu)


@app.route('/mem')
def show_mem():
    dt, cpu, mem, swap, proc, disk_header, disk = monitoring()
    all_mem = Mem.query.order_by(Mem.dt.desc()).limit(20).all()
    return render_template('mem.html', mem=mem, all_mem=all_mem)


@app.route('/swap')
def show_swap():
    dt, cpu, mem, swap, proc, disk_header, disk = monitoring()
    all_swap = Swap.query.order_by(Swap.dt.desc()).limit(20).all()
    return render_template('swap.html', swap=swap, all_swap=all_swap)


@app.route('/disk')
def show_disk():
    dt, cpu, mem, swap, proc, disk_header, disk = monitoring()
    all_disk = Disk.query.order_by(Disk.dt.desc()).limit(20).all()
    print(disk_header)
    print()
    print(disk)
    print()
    print(all_disk)
    return render_template('disk.html', disk=disk, disk_header=disk_header, all_disk=all_disk)


@app.route('/process')
def show_process():
    dt, cpu, mem, swap, proc, disk_header, disk = monitoring()
    return render_template('process.html', proc=proc)


def monitoring():
    dt = datetime.now()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.16.108.128', username='kinan', password='1827')
    cpu = get_cpu(ssh)
    disk_header, disk = get_disk(ssh)
    mem = get_mem(ssh)
    swap = get_swap(ssh)
    proc = get_processes(ssh)
    ssh.close()
    proc = [p for p in proc if float(p['%CPU']) > 0 or float(p["%MEM"]) > 10]

    add_disk(disk, dt)
    add_mem(mem, dt)
    add_swap(swap, dt)
    add_cpu(cpu, dt)
    add_proc(proc, dt)
    
    return dt, cpu, mem, swap, proc, disk_header, disk


@app.route('/')
def base():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
