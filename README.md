## Synopsis

This project is a Django-based system for managing packages on CentOS and Ubuntu systems. RHEL and Debian shouldn't be too hard to add.

## Motivation

This project attempts to solve patch management issues for sysadmins and others using Linux systems in their estate; it's intended to be dropped on to an Ansible host as it uses passwordless sudo for its functions.

## Prerequisites

- A MySQL server with a database created and a user / pass set (other backends may work if you wish to try but are untested - see https://docs.djangoproject.com/en/1.11/ref/settings/)
- Python3+ (It's 2017, why are we still using 2.7?)
- Paramiko (pip3 install paramiko, http://www.paramiko.org/)
- mysqlclient (pip3 install mysqlclient, https://github.com/PyMySQL/mysqlclient-python)
- Django 1.10+ (pip3 install django, https://www.djangoproject.com/)
- Passwordless sudo on the servers to be managed 

## Installation

Clone this repo to a directory, edit the settings.py file to reflect your database setup, then run the following from the directory *using python 3*:

`python manage.py runserver 0.0.0.0:8000`

Access the index page at <webserver address>:8000/first_app .

## Contributors

Project Lead - Matt North (@jackandhishat on Twitter)

## License

GPLv3
