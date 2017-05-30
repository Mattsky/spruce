## Synopsis

This project is a Django-based system for managing packages on CentOS / RHEL and Ubuntu / Debian systems.

## Motivation

This project attempts to solve patch management issues for sysadmins and others using Linux systems in a large estate; it's intended to be dropped on to an Ansible host as it uses passwordless sudo for its functions.

## Prerequisites

- A MySQL server with a database created and a user / pass set
- Python3+ (It's 2017, why are we still using 2.7?)
- Paramiko (pip3 install paramiko, http://www.paramiko.org/)
- mysqlclient (pip3 install mysqlclient, https://github.com/PyMySQL/mysqlclient-python)
- Django 1.10+ (pip3 install django, https://www.djangoproject.com/)
- Passwordless sudo on the servers to be managed 

## Installation

Clone this repo to a directory, then run the following from the directory *using python 3*:
python manage.py runserver 0.0.0.0:8000

## Contributors

Matt North (@jackandhishat on Twitter)

## License

TBD
