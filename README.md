## Synopsis

This project is a Django-based system for managing packages on CentOS and Ubuntu systems. RHEL and Debian shouldn't be too hard to add and are on the roadmap.

## Motivation

This project attempts to aid sysadmins with patch management issues when using Linux systems in their estate; it's intended to be dropped on to an Ansible host as it uses passwordless sudo for its functions.

## WARNING

This project is still very much in development and things like debug mode settings, hardcoded security tokens etc. reflect that. Be sure to review the checklist here if you intend on using this in production before it's properly ready to do so: https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

## Prerequisites

- A MySQL server with a database created and a user / pass set (other backends may work if you wish to try but are untested - see https://docs.djangoproject.com/en/1.11/ref/settings/)
- libmysqlclient-dev and python-dev packages (Ubuntu)
- Python3+ 
- Paramiko (pip3 install paramiko, http://www.paramiko.org/)
- mysqlclient (pip3 install mysqlclient, https://github.com/PyMySQL/mysqlclient-python)
- Django 1.10+ (pip3 install django, https://www.djangoproject.com/)
- Passwordless sudo on the servers to be managed - this is intended to be dropped on to an Ansible command server for ease of use

## Installation

Clone this repo to a directory, edit the master_project/settings.py file to reflect your database setup, HOMEDIR, KEYFILE (SSH key settings) and ALLOWED_HOST settings then run the following from the directory *using python 3*:

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py runserver 0.0.0.0:8000`

Access the index page at <webserver address>:8000/spruce and log in using the new superuser account. You can manage users at <webserver address>:8000/admin

## Contributors

Project Lead - Matt North (@jackandhishat on Twitter)

## License

GPLv3
