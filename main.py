from flask import Flask
from utilities import *
app = Flask(__name__)

@app.route('/')
def main_route():
    return 'Hello Moto'


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
