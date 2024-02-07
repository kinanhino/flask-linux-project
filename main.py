from flask import Flask
import paramiko

app = Flask(__name__)

@app.route('/')
def main_route():
    return 'Hello Moto'

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

@app.route('/cpu-util')
def cpu_utilization():
    # Replace with the correct details of your target VM
    host = "172.16.108.128"
    port = 22  # default SSH port
    username = "kinan"
    password = "1827"
    cpu_usage = get_remote_cpu_utilization(host, port, username, password)
    return f"CPU Utilization: {cpu_usage}"

if __name__ == '__main__':
    app.run(debug=True)
