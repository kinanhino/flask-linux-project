from utils import db


class Disk(db.Model):
    disk_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    Filesystem = db.Column(db.String(50), nullable=False)
    Size = db.Column(db.String(10), nullable=False)
    Used = db.Column(db.String(10), nullable=False)
    Avail = db.Column(db.String(10), nullable=False)
    Use = db.Column(db.String(10), nullable=False)
    Mounted_on = db.Column(db.String(50), nullable=False)
    mac = db.Column(db.String(50), nullable=False)


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
    mac = db.Column(db.String(50), nullable=False)


class Mem(db.Model):
    mem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    cache = db.Column(db.Float, nullable=False)
    mac = db.Column(db.String(50), nullable=False)


class Swap(db.Model):
    swap_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    available = db.Column(db.Float, nullable=False)
    mac = db.Column(db.String(50), nullable=False)


class Process(db.Model):
    proc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt = db.Column(db.DateTime, nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    cpu = db.Column(db.Float, nullable=False)
    mem = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(5), nullable=False)
    command = db.Column(db.String(50), nullable=False)
    mac = db.Column(db.String(50), nullable=False)
