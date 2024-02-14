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


def get_monitoring_data():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.16.137.128', username='kali', password='kali')
    stdin, stdout, stderr = ssh.exec_command('top -b -n 1')
    top_data = stdout.read().decode().strip()
    top_data = top_data.split('\n')

    for i in range(len(top_data)):
        top_data[i] = top_data[i].split()

    ssh.close()

    cpu = {
        "us": float(top_data[2][1]),
        "sy": float(top_data[2][3]),
        "ni": float(top_data[2][5]),
        "id": float(top_data[2][7]),
        "wa": float(top_data[2][9]),
        "hi": float(top_data[2][11]),
        "si": float(top_data[2][13]),
        "st": float(top_data[2][15])
    }
    mem = {
        "total": float(top_data[3][3]),
        "free": float(top_data[3][5]),
        "used": float(top_data[3][7]),
        "cache": float(top_data[3][9])
    }
    swap = {
        "total": float(top_data[4][2]),
        "free": float(top_data[4][4]),
        "used": float(top_data[4][6]),
        "available": float(top_data[4][8])
    }
    proc = [] #list of dict of process
    for p in top_data[7:]:
        d = {}
        d[top_data[6][0]] = int(p[0]) #PID
        d[top_data[6][1]] = p[1] #USER
        d[top_data[6][7]] = p[7] #STAT
        d[top_data[6][8]] = float(p[8]) #%CPU
        d[top_data[6][9]] = float(p[9]) #%MEM
        d[top_data[6][11]] = p[11] #COMMAND
        proc.append(d)

    return cpu, mem, swap, proc, datetime.now()


def add_cpu(cpu,date):
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
    available = swap["available"]
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





@app.route('/')
def monitoring():
    try:
        cpu, mem, swap, proc, date = get_monitoring_data()
        proc = [p for p in proc if p['%CPU']>0 or p['%MEM']>10]
        add_cpu(cpu, date)
        add_mem(mem, date)
        add_swap(swap, date)
        add_proc(proc, date)
    except:
        cpu = Cpu.query.order_by(Cpu.dt.desc()).first()
        mem = Mem.query.order_by(Mem.dt.desc()).first()
        swap = Swap.query.order_by(Swap.dt.desc()).first()
        proc = []
        date = datetime.now()

    all_cpu = Cpu.query.all()
    all_mem = Mem.query.all()
    all_swap = Swap.query.all()


    return render_template("homepage.html",cpu=cpu, mem=mem, swap=swap, proc=proc, date=date, all_cpu=all_cpu, all_mem=all_mem, all_swap=all_swap)


"""
@app.route('/update-data')
def update_data():
    try:
        cpu, mem, swap, proc, date = get_monitoring_data()
        proc = [p for p in proc if p['%CPU'] > 0 or p['%MEM'] > 10]
        add_cpu(cpu, date)
        add_mem(mem, date)
        add_swap(swap, date)
        add_proc(proc, date)
    except:
        cpu = Cpu.query.order_by(Cpu.dt.desc()).first()
        mem = Mem.query.order_by(Mem.dt.desc()).first()
        swap = Swap.query.order_by(Swap.dt.desc()).first()
        proc = []
        date = datetime.now()

    all_cpu = Cpu.query.all()
    all_mem = Mem.query.all()
    all_swap = Swap.query.all()

    return jsonify(cpu=cpu, mem=mem, swap=swap, proc=proc, date=date)
"""


if __name__ == '__main__':
    app.run(debug=True, port=5001)
