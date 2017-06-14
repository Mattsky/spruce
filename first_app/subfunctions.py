from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection, transaction
from django.conf import settings
from django.core.files import File
import paramiko
import re, time, datetime, os

def sshtest_comm(target_address, TEST_USER, keyfile):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(target_address, username=TEST_USER, key_filename=keyfile, timeout=10)
    stdin, stdout, stderr = ssh.exec_command('cat /etc/issue')
    output = stdout.read()
    return(output)

def scan_systems(system_list):
	print(YAY)