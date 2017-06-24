# Spruce - a tool to help manage system software states.
# Copyright (C) 2017 Matt North

# This file is part of Spruce.

# Spruce is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Spruce is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Spruce.  If not, see <http://www.gnu.org/licenses/>.

from spruce.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection, transaction
from spruce.ubuntu_functions import *
from spruce.centos7_functions import *
from django.conf import settings
from django.core.files import File
import paramiko
import re, time, datetime
import multiprocessing

def os_ident(ssh):
    OS = ''
    Version = ''
    try:
        sftp = ssh.open_sftp()
        try:
            remote_file = sftp.open('/etc/redhat-release')
            for line in remote_file:
                if 'CentOS' in line:
                    OS = str.split(line)[0]
                    Version = str.split(line)[3]
                    Version = Version.split('.')[0]
                    osinfo = [OS, Version]
                    return(osinfo)
                
        except IOError:
            pass

        try:
            remote_file = sftp.open('/etc/issue')
            for line in remote_file:
                if 'Ubuntu' in line:
                    OS = str.split(line)[0]
                    Version = str.split(line)[1]
                    Version = '.'.join(Version.split('.',2)[0:2])
                    osinfo = [OS, Version]
                    return(osinfo)

        except IOError:
            print("File not found!")

    except paramiko.SSHException:
        print("Connection error")

def get_hostname(ssh):
    try:
        stdin, stdout, stderr = ssh.exec_command('hostname')
        sys_hostname = stdout.read()
        return(sys_hostname)
    except:
        print("ERROR")

def rescan(scan_address, scan_port, AUTH_USER, keyfile):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Delete existing info prior to refresh and recreate, just in case
    Hosts.objects.filter(hostaddr=scan_address).delete()
    

    ssh.connect(scan_address, port=int(scan_port), username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
            
    if 'CentOS' in os_id[0]:
        try:
            # Install required packages for functionality
            stdin, stdout, stderr = ssh.exec_command('sudo yum -y install yum-versionlock')
            exit_status = stdout.channel.recv_exit_status()
            host_entry = Hosts(hostaddr=scan_address, hostport=scan_port)
            host_entry.save()
            host_address = Hosts.objects.only('hostaddr').get(hostaddr=scan_address)
            
            host_name = get_hostname(ssh)
            #Strip whitespace from end of hostname
            host_name = host_name.rstrip()
            host_info_entry = HostInfo(host_addr=host_address, host_name=host_name, os_name=os_id[0], os_version=os_id[1])
            host_info_entry.save()
            centos_installed_packages = centos7_get_all_installed_packages(ssh)
            centos_converted_package_list = []
            for x in centos_installed_packages:
                centos_converted_package_list.append(InstalledPackageList(host_addr=host_address, package=x[0], currentver=x[2]))
            InstalledPackageList.objects.bulk_create(centos_converted_package_list)
            centos_held_packages = centos7_get_locked_packages(ssh)
            centos_converted_held_packages = []
            for x in centos_held_packages:
                centos_converted_held_packages.append(HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1]))
            HeldPackageList.objects.bulk_create(centos_converted_held_packages)
            centos_update_packages = centos7_get_package_updates(ssh)
            centos_converted_update_list = []
            for x in centos_update_packages:
                for z in centos_installed_packages:
                    if x[0] in z:
                        current_package_version = z[2]
                centos_converted_update_list.append(UpdateablePackageList(host_addr=host_address,package=x[0],currentver=current_package_version,newver=x[2]))
            UpdateablePackageList.objects.bulk_create(centos_converted_update_list)    
                
        except:
            print("PROBLEM SCANNING CENTOS HOST!")

    if 'Ubuntu' in os_id[0]:
        try:
            host_entry = Hosts(hostaddr=scan_address, hostport=scan_port)
            host_entry.save()
            host_address = Hosts.objects.only('hostaddr').get(hostaddr=scan_address)
            
            host_name = get_hostname(ssh)
            #Strip whitespace from end of hostname
            host_name = host_name.rstrip()
            host_info_entry = HostInfo(host_addr=host_address, host_name=host_name, os_name=os_id[0], os_version=os_id[1])
            host_info_entry.save()
            ubuntu_installed_packages = ubuntu_get_all_installed_packages(ssh)
            ubuntu_converted_package_list = []
            for x in ubuntu_installed_packages:
                ubuntu_converted_package_list.append(InstalledPackageList(host_addr=host_address, package=x[0], currentver=x[1]))
            InstalledPackageList.objects.bulk_create(ubuntu_converted_package_list)
            ubuntu_held_packages = ubuntu_get_held_packages(ssh)
            ubuntu_converted_held_packages = []
            for x in ubuntu_held_packages:
                ubuntu_converted_held_packages.append(HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1]))
            HeldPackageList.objects.bulk_create(ubuntu_converted_held_packages)
            ubuntu_update_packages = ubuntu_get_package_updates(ssh)
            ubuntu_converted_updates_list = []
            for x in ubuntu_update_packages:
                ubuntu_converted_updates_list.append(UpdateablePackageList(host_addr=host_address,package=x[0],currentver=x[1],newver=x[2]))
            UpdateablePackageList.objects.bulk_create(ubuntu_converted_updates_list)
        except:
            print("PROBLEM SCANNING UBUNTU HOST!")

 

def unhold_packages(host_id, packages_to_unhold, TEST_ADDR, AUTH_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(TEST_ADDR, username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        
        ubuntu_unhold_packages(ssh, packages_to_unhold)
        for x in packages_to_unhold:
            HeldPackageList.objects.filter(host_addr=host_id).filter(package=x).delete()
        held_packages = ubuntu_get_held_packages(ssh)

    if 'CentOS' in os_id[0]:
        centos7_unlock_packages(ssh, packages_to_unhold)
        for x in packages_to_unhold:
            HeldPackageList.objects.filter(host_addr=host_id).filter(package=x).delete()
        held_packages = centos7_get_locked_packages(ssh)

def update_packages(host_id, packages_to_update, TEST_ADDR, AUTH_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host_address = Hosts.objects.only('hostaddr').get(hostaddr=host_id)
    ssh.connect(TEST_ADDR, username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        ubuntu_apply_package_updates(ssh, packages_to_update)
        held_packages = ubuntu_get_held_packages(ssh)
        UpdateablePackageList.objects.filter(host_addr=host_id).delete()
        ubuntu_update_packages = ubuntu_get_package_updates(ssh)
        for x in ubuntu_update_packages:
            update_package_entry = UpdateablePackageList(host_addr=host_address,package=x[0],currentver=x[1],newver=x[2])
            update_package_entry.save()

    if 'CentOS' in os_id[0]:
        centos7_update_packages(ssh, packages_to_update)
        held_packages = centos7_get_locked_packages(ssh)
        UpdateablePackageList.objects.filter(host_addr=host_id).delete()
        centos_update_packages = centos7_get_package_updates(ssh)
        for x in centos_update_packages:
            for z in centos_update_packages:
                if x[0] in z:
                    current_package_version = z[2]
            update_package_entry = UpdateablePackageList(host_addr=host_address,package=x[0],currentver=current_package_version,newver=x[2])
            update_package_entry.save()

def hold_packages(host_id, packages_to_hold, TEST_ADDR, AUTH_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_address = Hosts.objects.only('hostaddr').get(hostaddr=host_id)
    ssh.connect(TEST_ADDR, username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        ubuntu_hold_packages(ssh, packages_to_hold)
        HeldPackageList.objects.filter(host_addr=host_address).delete()
        ubuntu_held_packages = ubuntu_get_held_packages(ssh)
        for x in ubuntu_held_packages:
            held_package_entry = HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1])
            held_package_entry.save()

    if 'CentOS' in os_id[0]:
        centos7_lock_packages(ssh, packages_to_hold)
        HeldPackageList.objects.filter(host_addr=host_address).delete()
        centos_held_packages = centos7_get_locked_packages(ssh)
        for x in centos_held_packages:
            held_package_entry = HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1])
            held_package_entry.save()

def delete_info(scan_address):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Delete existing info - this cascades down to all other linked tables (foreign keys)
    Hosts.objects.filter(hostaddr=scan_address).delete()

def get_update_history(TEST_ADDR, AUTH_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(TEST_ADDR, username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'CentOS' in os_id[0]:
        update_history = centos_get_update_history(ssh)
        return(update_history)

    if 'Ubuntu' in os_id[0]:
        update_history = ubuntu_get_update_history(ssh)
        return(update_history)



def rollback_update(transact_id, TEST_ADDR, AUTH_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(TEST_ADDR, username=AUTH_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'CentOS' in os_id[0]:
        try:
            rollback_status = centos7_roll_back_update(ssh, transact_id)
            return(rollback_status)
        except:
            return("PROBLEM.")

    if 'Ubuntu' in os_id[0]:
        try:
            rollback_status = ubuntu_roll_back_update(ssh, transact_id)
            return(rollback_status)
        except:
            return("UBUNTU ROLLBACK PROBLEM.")


def multi_system_scan(system_list, AUTH_USER, keyfile):
    
    try:
        plist = []
        # Delete existing info otherwise scans hang. Not efficient - needs looking in to. Maybe search existing hosts
        # in db and remove from list if found, then pass final list into multiprocessing call below?
        for x in system_list:
            delete_info(x[0])

        for i in range(0, len(system_list)):
            scan_address = system_list[i][0]
            scan_port = system_list[i][1]
            p = multiprocessing.Process(target = rescan(scan_address, scan_port, AUTH_USER, keyfile))
            p.start()
            plist.append(p)

        for p in plist:
            p.join() # Wait for all processes to finish

    except:
        print("Multiscan failed.")

def multi_system_rescan(system_list, AUTH_USER, keyfile):
    
    try:
        plist = []
        
        for x in system_list:
            delete_info(x[0])

        for i in range(0, len(system_list)):
            scan_address = system_list[i][0]
            scan_port = system_list[i][1]
            p = multiprocessing.Process(target = rescan(scan_address, scan_port, AUTH_USER, keyfile))
            p.start()
            plist.append(p)

        for p in plist:
            p.join() # Wait for all processes to finish

    except:
        print("Multi rescan failed.")
