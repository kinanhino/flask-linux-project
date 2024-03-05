def get_mac_address(ssh):
    stdin, stdout, stderr = ssh.exec_command("ifconfig | grep -o -E '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' ")
    return stdout.read().decode()


def get_cpu(ssh):
    stdin, stdout, stderr = ssh.exec_command('top -b -n 1 | grep Cpu')
    data = stdout.read().decode().strip().split(",")
    data[0] = data[0].split()[1]
    for i in range(1, len(data)):
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
            'Use': d[4],
            'Mounted_on': d[5]
        }
        disk_data.append(d_dict)
    return disk_headers, disk_data


def get_processes(ssh, date):
    stdin, stdout, stderr = ssh.exec_command(r"top -n1 -b | grep -E '^\s*[0-9]+|^\s*%CPU'")
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

