import os

from flask import Flask, jsonify, render_template
import paramiko
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from dotenv import load_dotenv
load_dotenv()

class Disk(db.Model):
    disk_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    Filesystem = db.Column(db.String(50), nullable=False)
    Size = db.Column(db.String(10), nullable=False)
    Used = db.Column(db.String(10), nullable=False)
    Avail = db.Column(db.String(10), nullable=False)
    Use = db.Column(db.String(10), nullable=False)
    Mounted_on = db.Column(db.String(50), nullable=False)


class Cpu(db.Model):
    cpu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    us = db.Column(db.Float, nullable=False)
    sy = db.Column(db.Float, nullable=False)
    ni = db.Column(db.Float, nullable=False)
    id = db.Column(db.Float, nullable=False)
    wa = db.Column(db.Float, nullable=False)
    hi = db.Column(db.Float, nullable=False)
    si = db.Column(db.Float, nullable=False)
    st = db.Column(db.Float, nullable=False)


class Mem(db.Model):
    mem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    cache = db.Column(db.Float, nullable=False)


class Swap(db.Model):
    swap_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    available = db.Column(db.Float, nullable=False)


class Process(db.Model):
    proc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    cpu = db.Column(db.Float, nullable=False)
    mem = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(5), nullable=False)
    command = db.Column(db.String(50), nullable=False)


def get_cpu(ssh):
    stdin, stdout, stderr = ssh.exec_command('top -b -n 1 | grep Cpu')
    data = stdout.read().decode().strip().split(",")
    data[0]= data[0].split()[1]
    for i in range(1,len(data)):
        data[i] = data[i].split()[0]
    cpu = {
        "us": float(data[0]),
        "sy": float(data[1]),
        "ni": float(data[2]),
        "id": float(data[3]),
        "wa": float(data[4]),
        "hi": float(data[5]),
        "si": float(data[6]),
        "st": float(data[7])
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


def get_processes(ssh, date):
    stdin, stdout, stderr = ssh.exec_command("top -n1 -b | grep -E '^\s*[0-9]+|^\s*%CPU'")
    top_data = stdout.read().decode().strip()
    top_data = top_data.split('\n')
    for i in range(len(top_data)):
        top_data[i] = top_data[i].split()
    proc = []
    for p in top_data:
        d = {
            'PID': p[0],
            'USER': p[1],
            'S': p[7],
            '%CPU': p[8],
            '%MEM': p[9],
            'COMMAND': p[11],
            'dt': date.strftime('%Y-%m-%d %H:%M:%S')
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
    cpu = monitoring("cpu")
    all_cpu = Cpu.query.order_by(Cpu.dt.desc()).limit(20).all()
    return render_template('cpu.html', cpu=cpu, all_cpu=all_cpu)

@app.route('/refresh_cpu')
def refresh_cpu():
    cpu = monitoring("cpu")
    all_cpu = [cpu_obj.__dict__ for cpu_obj in Cpu.query.order_by(Cpu.dt.desc()).limit(20).all()]
    all_cpu = all_cpu[::-1]
    for cpu_data in all_cpu:
        cpu_data.pop('_sa_instance_state', None)
    return jsonify({
        "cpu": cpu,
        "all_cpu": all_cpu
    })

@app.route('/mem')
def show_mem():
    mem = monitoring("mem")
    all_mem = Mem.query.order_by(Mem.dt.desc()).limit(20).all()
    return render_template('mem.html', mem=mem, all_mem=all_mem)


@app.route('/refresh_mem')
def refresh_mem():
    mem = monitoring("mem")
    all_mem = [mem_obj.__dict__ for mem_obj in Mem.query.order_by(Mem.dt.desc()).limit(20).all()]
    all_mem = all_mem[::-1]
    for mem_data in all_mem:
        mem_data.pop('_sa_instance_state', None)
    return jsonify({
        "mem": mem,
        "all_mem": all_mem
    })

@app.route('/swap')
def show_swap():
    swap = monitoring("swap")
    all_swap = Swap.query.order_by(Swap.dt.desc()).limit(20).all()
    return render_template('swap.html', swap=swap, all_swap=all_swap)

@app.route('/refresh_swap')
def refresh_swap():
    swap = monitoring("swap")
    all_swap = [swap_obj.__dict__ for swap_obj in Swap.query.order_by(Swap.dt.desc()).limit(20).all()]
    all_swap = all_swap[::-1]
    for swap_data in all_swap:
        swap_data.pop('_sa_instance_state', None)
    return jsonify({
        "swap": swap,
        "all_swap": all_swap
    })


@app.route('/disk')
def show_disk():
    disk_header, disk, dt = monitoring("disk")
    all_disk = Disk.query.order_by(Disk.dt.desc()).limit(20).all()
    return render_template('disk.html', disk=disk, disk_header=disk_header, all_disk=all_disk)


@app.route('/refresh_disk')
def refresh_disk():
    disk_header, disk, dt = monitoring("disk")
    all_disk = [disk_obj.__dict__ for disk_obj in Disk.query.where(Disk.dt==dt).all()]
    for disk_data in all_disk:
        disk_data.pop('_sa_instance_state', None)
    return jsonify({
        "all_disk": all_disk
    })


@app.route('/refresh_process')
def refresh_process():
    proc = monitoring("proc")
    return jsonify(proc)


@app.route('/process')
def show_process():
    proc = monitoring("proc")
    return render_template('process.html', proc=proc)


def monitoring(info):
    dt = datetime.now()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.getenv('IP_ADDRESS')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    ssh.connect(host, username=username, password=password)
    cpu = get_cpu(ssh)
    disk_header, disk = get_disk(ssh)
    mem = get_mem(ssh)
    swap = get_swap(ssh)
    proc = get_processes(ssh, dt)
    ssh.close()
    proc2 = [p for p in proc if float(p['%CPU']) > 0 or float(p["%MEM"]) > 10]

    # if cpu['us'] > 10 or mem['used'] > (mem['total']/2) or swap['used'] > (swap['total']/2):
    #     pass
    add_disk(disk, dt)
    add_mem(mem, dt)
    add_swap(swap, dt)
    add_cpu(cpu, dt)
    add_proc(proc2, dt)

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

@app.route('/')
def base():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
