# Spruce: helping you manage systems.

<img src="http://ccrg.co.uk/spruce_logo.png" align="left" hspace="10" vspace="6">

Spruce is a Django-based application for managing packages on Linux systems. So far Ubuntu and CentOS are supported, with Debian and RHEL on the roadmap.

## Prerequisites

- SSH key based passwordless sudo access to the servers to be managed (this is intended to be dropped on to an Ansible command server for ease of use)
- A MySQL server with a database created and a user / pass set (other backends may work if you wish to try but are untested - see https://docs.djangoproject.com/en/1.11/ref/settings/)
- libmysqlclient-dev and python-dev packages (Ubuntu)
- Python3+ 
- Paramiko (pip3 install paramiko, http://www.paramiko.org/)
- mysqlclient (pip3 install mysqlclient, https://github.com/PyMySQL/mysqlclient-python)
- Django 1.10+ (pip3 install django, https://www.djangoproject.com/)

## Installation

Clone this repo to a directory:

`git clone git@github.com:Mattsky/spruce.git`

Edit the master_project/settings.py file to reflect your database setup and set the following extra variables:

- AUTH_USER (SSH keyfile owner's username)
- HOMEDIR (SSH keyfile location, defaults to ~/.ssh)
- KEYFILE (SSH keyfile name) 
- ALLOWED_HOST (the IP address(es) that Django should respond to requests for)

Run the following commands from the directory *using python 3*:

`python manage.py migrate` (prepare database)

`python manage.py createsuperuser` (create admin user - do this at least, otherwise you won't be able to log in)

`python manage.py runserver 0.0.0.0:8000` (start the server to listen on all available ports. Change as required.)

Access the index page at `webserver_address:8000/spruce` and log in using the new superuser account. 

You can also manage users at `webserver_address:8000/admin`.

## Features and Usage

Spruce has 3 main functions: Index, Scan, and Upload.

### Index

The index shows the list of systems that Spruce holds information on. From here, you can access and manipulate:

- General system info - OS, Version, IP, SSH port etc.
- Available software updates - just like it says on the tin
- Version-locked / pinned packages - see what packages are being held at a specific version
- Installed packages - see what's installed and hold the versions
- Recent system update history - view recent installation information and selectively roll back updates

### Scan

From here you can scan a single system by entering the IP address and SSH port.

### Upload

Here you can upload an Ansible inventory file, and Spruce will attempt to contact all of the hosts defined therein and collect information in multithreaded fashion.

## WARNINGS

This project is still very much in development and things like debug mode settings, hardcoded security tokens etc. reflect that. Consider SSL termination and be sure to review the checklist here if you intend on using this in production before it's properly ready to do so: https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

When using the update rollback functionality, be aware that this depends on the system's own ability to roll back installs, resolve dependencies etc. While this does work, there is a non-zero chance that it could cause strange things to happen, or even break the system. Snapshotting / backing up before using this is generally advised, and we take no responsibility if anything breaks spectacularly as a result of using it.

## Contributors

Project Lead - Matt North (@jackandhishat on Twitter)

## License

GPLv3
