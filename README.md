# Monitoring System README
This project is a web-based monitoring dashboard developed using Flask, SQLAlchemy, and Paramiko.
It allows users to monitor general information about a linux system via SSH.

## Components

### 1. Flask Web Application

The monitoring system is built using the Flask web framework in Python. It provides a user interface for viewing system resource data.

### 2. SQLAlchemy

SQLAlchemy is used as an Object-Relational Mapping (ORM) tool to interact with the SQLite database where system resource data is stored.

### 3. Paramiko

Paramiko is utilized to establish SSH connections with remote machines for collecting system resource data.

## Database Schema

The SQLite database (`site.db`) comprises several tables to store different types of system resource data:

1. **Disk**: Records disk usage information.
2. **CPU**: Stores CPU usage information.
3. **Memory (Mem)**: Stores memory data.
4. **Swap**: Records swap memory data.
5. **Process**: Stores information about running processes.

## Functionality

The monitoring system perform the following tasks:

1. **Collect System Resource Data**: It fetches CPU, memory, swap, disk, and process data from remote machines via SSH.

2. **Store Data**: The collected data is stored in the SQLite database for historical analysis and visualization.

3. **Display Data**: Users can view real-time and historical system resource data via the web interface provided by the Flask application.

## Usage

1. **Login**: Users need to provide the IP address, username, and password of the target machine to establish an SSH connection. Once logged in, they can access the monitoring dashboard.

2. **Dashboard**: After logging in, users can view real-time system resource usage statistics such as CPU, memory, swap, disk, and processes.

3. **Refresh Data**: Automatically refresh the displayed data every 10 seconds to see the most recent information without reloading the page.

4. **Navigation**: Users can navigate between different resource views using the navigation links provided in the web interface.

## Deployment

To deploy the monitoring system:

1. Ensure all dependencies listed in `requirements.txt` are installed.
2. Run the Flask application using `python app.py`.
3. Access the application via a web browser at the specified port (default is `http://localhost:5001`).

## Database Initialization and Migration

Before running the application for the first time, you need to initialize the database and perform any necessary migrations. Follow these steps:

1. Ensure that you have the required permissions and access to the SQLite database (site.db) file.
2. Open a terminal or command prompt.
3. Navigate to the project directory.
4. Run the following commands to initialize the database and perform migrations:
   1. flask db init
   2. flask db migrate
   3. flask db upgrade
   
## Notes

- Make sure SSH is enabled on the target machines and the necessary permissions are granted for remote access.


