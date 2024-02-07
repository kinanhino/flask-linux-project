import paramiko
def get_remote_cpu_utilization(host, port, username, password):
    # Command to get CPU utilization. Adjust based on the target system.
    command = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{print 100 - $1\"%\"}'"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        cpu_utilization = stdout.read().decode().strip()
        ssh.close()
        return cpu_utilization
    except Exception as e:
        print(f"Failed to connect or execute command: {e}")
        return "Error"