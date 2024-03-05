from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
import paramiko
from flask_migrate import Migrate
import socket
from models import *
from main_function import monitoring
from get_functions import get_mac_address

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.secret_key = "abcdfdfdsfgdfgfdgd"
db.init_app(app)
migrate = Migrate(app, db)
db.session.flag = "none"


@app.route('/cpu')
def show_cpu():
    if db.session.flag == "flex":
        cpu = monitoring("cpu")
        all_cpu = Cpu.query.filter(Cpu.mac == db.session.mac).order_by(Cpu.dt.desc()).limit(20).all()
        return render_template('cpu.html', cpu=cpu, all_cpu=all_cpu)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/refresh_cpu')
def refresh_cpu():
    if db.session.flag == "flex":
        cpu = monitoring("cpu")
        all_cpu = [cpu_obj.__dict__ for cpu_obj in
                   Cpu.query.filter(Cpu.mac == db.session.mac).order_by(Cpu.dt.desc()).limit(20).all()]
        all_cpu = all_cpu[::-1]
        for cpu_data in all_cpu:
            cpu_data.pop('_sa_instance_state', None)
        return jsonify({
            "cpu": cpu,
            "all_cpu": all_cpu
        })
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/mem')
def show_mem():
    if db.session.flag == "flex":
        mem = monitoring("mem")
        all_mem = Mem.query.filter(Mem.mac == db.session.mac).order_by(Mem.dt.desc()).limit(20).all()
        return render_template('mem.html', mem=mem, all_mem=all_mem)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/refresh_mem')
def refresh_mem():
    if db.session.flag == "flex":
        mem = monitoring("mem")
        all_mem = [mem_obj.__dict__ for mem_obj in
                   Mem.query.filter(Mem.mac == db.session.mac).order_by(Mem.dt.desc()).limit(20).all()]
        all_mem = all_mem[::-1]
        for mem_data in all_mem:
            mem_data.pop('_sa_instance_state', None)
        return jsonify({
            "mem": mem,
            "all_mem": all_mem
        })
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/swap')
def show_swap():
    if db.session.flag == "flex":
        swap = monitoring("swap")
        all_swap = Swap.query.filter(Swap.mac == db.session.mac).order_by(Swap.dt.desc()).limit(20).all()
        return render_template('swap.html', swap=swap, all_swap=all_swap)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/refresh_swap')
def refresh_swap():
    if db.session.flag == "flex":
        swap = monitoring("swap")
        all_swap = [swap_obj.__dict__ for swap_obj in
                    Swap.query.filter(Swap.mac == db.session.mac).order_by(Swap.dt.desc()).limit(20).all()]
        all_swap = all_swap[::-1]
        for swap_data in all_swap:
            swap_data.pop('_sa_instance_state', None)
        return jsonify({
            "swap": swap,
            "all_swap": all_swap
        })
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/disk')
def show_disk():
    if db.session.flag == "flex":
        disk_header, disk, dt = monitoring("disk")
        all_disk = Disk.query.filter(Disk.mac == db.session.mac).order_by(Disk.dt.desc()).limit(20).all()
        return render_template('disk.html', disk=disk, disk_header=disk_header, all_disk=all_disk)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/refresh_disk')
def refresh_disk():
    if db.session.flag == "flex":
        disk_header, disk, dt = monitoring("disk")
        all_disk = [disk_obj.__dict__ for disk_obj in
                    Disk.query.filter(Disk.mac == db.session.mac).where(Disk.dt == dt).all()]
        for disk_data in all_disk:
            disk_data.pop('_sa_instance_state', None)
        return jsonify({
            "all_disk": all_disk
        })
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/refresh_process')
def refresh_process():
    if db.session.flag == "flex":
        proc = monitoring("proc")
        return jsonify(proc)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/process')
def show_process():
    if db.session.flag == "flex":
        proc = monitoring("proc")
        return render_template('process.html', proc=proc)
    flash("You must be logged first")
    return redirect(url_for('login', logged=db.session.flag))


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        host = request.form['ip_address']
        username = request.form['username']
        password = request.form['password']
        try:
            ssh.connect(host, username=username, password=password)
            db.session.mac = get_mac_address(ssh)
            db.session.ssh = ssh
            db.session.ip = host
            db.session.user = username
            db.session.flag = "flex"
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            # print(f"1 {e}")
            flash("Please check that your machine is running and ssh is enabled")
            return render_template('login.html', logged=db.session.flag)
        except paramiko.ssh_exception.AuthenticationException as e:
            # print(f"2 {e}")
            flash("Incorrect Information")
            flash("Please check your username and password and try again..")
            return render_template('login.html', logged=db.session.flag)
        except (paramiko.ssh_exception.SSHException, TimeoutError, socket.gaierror) as e:
            # print(f"3 {e}")
            flash("Something is wrong")
            flash("Please check your IP and that your machine is running and try again..")
            return render_template('login.html', logged=db.session.flag)
        return render_template('base.html', logged=db.session.flag, ip_addr=db.session.ip, username=db.session.user)
    if db.session.flag == "flex":
        return render_template('base.html', logged=db.session.flag, ip_addr=db.session.ip, username=db.session.user)
    else:
        return render_template('login.html', logged=db.session.flag)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
