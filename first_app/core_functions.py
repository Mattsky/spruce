from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection, transaction
from first_app.ubuntu_functions import *
from first_app.sql_functions import *
from first_app.centos7_functions import *
from django.conf import settings
from django.core.files import File
import paramiko
import re, time, datetime

def test_print9000():
    print("ROUTINE CALLED")

def os_ident(ssh):
    OS = ''
    Version = ''
    try:
        sftp = ssh.open_sftp()
        try:
            remote_file = sftp.open('/etc/redhat-release')
            for line in remote_file:
                #print(line)
                # CentOS Linux release 7.3.1611 (Core)
                if 'CentOS' in line:
                    OS = str.split(line)[0]
                    Version = str.split(line)[3]
                    Version = Version.split('.')[0]
                    #return(OS + ' ' + Version)
                    osinfo = [OS, Version]
                    return(osinfo)
                
        except IOError:
            pass

        try:
            remote_file = sftp.open('/etc/issue')
            for line in remote_file:
                #print(line)
                #Ubuntu 16.04.2 LTS \n \l
                if 'Ubuntu' in line:
                    OS = str.split(line)[0]
                    Version = str.split(line)[1]
                    Version = '.'.join(Version.split('.',2)[0:2])
                    #return(OS + ' ' + Version)
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

def rescan(scan_address, TEST_USER, keyfile):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Delete existing info prior to refresh and recreate, just in case
    Hosts.objects.filter(hostaddr=scan_address).delete()
    

    ssh.connect(scan_address, username=TEST_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    print(os_id)
            
    if 'CentOS' in os_id[0]:
        host_entry = Hosts(hostaddr=scan_address)
        host_entry.save()
        host_address = Hosts.objects.only('hostaddr').get(hostaddr=scan_address)
        #FIX THIS BIT - REARRANGE MODELS AS REQUIRED!
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        host_info_entry = HostInfo(host_addr=host_address, host_name=host_name, os_name=os_id[0], os_version=os_id[1])
        host_info_entry.save()
        centos_installed_packages = centos7_get_all_installed_packages(ssh)
        centos_converted_package_list = []
        for x in centos_installed_packages:
            #print(x)
            #installed_package_entry = InstalledPackageList(host_name=host_address, package=x[0], currentver=x[2])
            #installed_package_entry.save()
            centos_converted_package_list.append(InstalledPackageList(host_addr=host_address, package=x[0], currentver=x[2]))
        InstalledPackageList.objects.bulk_create(centos_converted_package_list)
        centos_held_packages = centos7_get_locked_packages(ssh)
        centos_converted_held_packages = []
        for x in centos_held_packages:
            #print(x)
            #held_package_entry = HeldPackageList(host_name=host_address,package=x[0],currentver=x[1])
            #held_package_entry.save()
            centos_converted_held_packages.append(HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1]))
        HeldPackageList.objects.bulk_create(centos_converted_held_packages)
        centos_update_packages = centos7_get_package_updates(ssh)
        centos_converted_update_list = []
        for x in centos_update_packages:
            #print(x)
            for z in centos_installed_packages:
                #print(z)
                if x[0] in z:
                    current_package_version = z[2]
            centos_converted_update_list.append(UpdateablePackageList(host_addr=host_address,package=x[0],currentver=current_package_version,newver=x[2]))
        UpdateablePackageList.objects.bulk_create(centos_converted_update_list)    
            #update_package_entry = UpdateablePackageList(host_name=host_address,package=x[0],currentver=current_package_version,newver=x[2])
            #update_package_entry.save()

    if 'Ubuntu' in os_id[0]:
        host_entry = Hosts(hostaddr=scan_address)
        host_entry.save()
        host_address = Hosts.objects.only('hostaddr').get(hostaddr=scan_address)
        #FIX THIS BIT - REARRANGE MODELS AS REQUIRED!
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        host_info_entry = HostInfo(host_addr=host_address, host_name=host_name, os_name=os_id[0], os_version=os_id[1])
        host_info_entry.save()
        ubuntu_installed_packages = ubuntu_get_all_installed_packages(ssh)
        ubuntu_converted_package_list = []
        for x in ubuntu_installed_packages:
            # BEGIN ORIGINAL WORKING CODE
            #print(x)
            #installed_package_entry = InstalledPackageList(host_name=host_address, package=x[0], currentver=x[1])
            #installed_package_entry.save()
            # END ORIGINAL WORKING CODE
            # BEGIN BULK CREATE CODE
            ubuntu_converted_package_list.append(InstalledPackageList(host_addr=host_address, package=x[0], currentver=x[1]))
        InstalledPackageList.objects.bulk_create(ubuntu_converted_package_list)
            # END BULK CREATE CODE
        ubuntu_held_packages = ubuntu_get_held_packages(ssh)
        ubuntu_converted_held_packages = []
        for x in ubuntu_held_packages:
            #print(x)
            #held_package_entry = HeldPackageList(host_name=host_address,package=x[0],currentver=x[1])
            #held_package_entry.save()
            ubuntu_converted_held_packages.append(HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1]))
        HeldPackageList.objects.bulk_create(ubuntu_converted_held_packages)
        ubuntu_update_packages = ubuntu_get_package_updates(ssh)
        ubuntu_converted_updates_list = []
        for x in ubuntu_update_packages:
            #print(x)
            #update_package_entry = UpdateablePackageList(host_name=host_address,package=x[0],currentver=x[1],newver=x[2])
            #update_package_entry.save()
            ubuntu_converted_updates_list.append(UpdateablePackageList(host_addr=host_address,package=x[0],currentver=x[1],newver=x[2]))
        UpdateablePackageList.objects.bulk_create(ubuntu_converted_updates_list)

 

def unhold_packages(host_id, packages_to_unhold, TEST_ADDR, TEST_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(TEST_ADDR, username=TEST_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        
        ubuntu_unhold_packages(ssh, packages_to_unhold)
        for x in packages_to_unhold:
            HeldPackageList.objects.filter(host_addr=host_id).filter(package=x).delete()
        held_packages = ubuntu_get_held_packages(ssh)
        #ubuntu_create_host_held_package_table(TEST_DB_HOST, TEST_DB, TEST_USER, TEST_PASS, syshost, held_packages)

    if 'CentOS' in os_id[0]:
        #for x in packages_to_unhold:
            #print(x)
        centos7_unlock_packages(ssh, packages_to_unhold)
        for x in packages_to_unhold:
            HeldPackageList.objects.filter(host_addr=host_id).filter(package=x).delete()
        held_packages = centos7_get_locked_packages(ssh)

def update_packages(host_id, packages_to_update, TEST_ADDR, TEST_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host_address = Hosts.objects.only('hostaddr').get(hostaddr=host_id)
    ssh.connect(TEST_ADDR, username=TEST_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        ubuntu_apply_package_updates(ssh, packages_to_update)
            #UpdateablePackageList.objects.filter(host_name=host_id).filter(package=x).delete()
        held_packages = ubuntu_get_held_packages(ssh)
        UpdateablePackageList.objects.filter(host_addr=host_id).delete()
        #ubuntu_create_host_held_package_table(TEST_DB_HOST, TEST_DB, TEST_USER, TEST_PASS, syshost, held_packages)
        ubuntu_update_packages = ubuntu_get_package_updates(ssh)
        for x in ubuntu_update_packages:
            #print(x)
            update_package_entry = UpdateablePackageList(host_addr=host_address,package=x[0],currentver=x[1],newver=x[2])
            update_package_entry.save()

    if 'CentOS' in os_id[0]:
        #print(type(packages_to_update))
        centos7_update_packages(ssh, packages_to_update)
            #UpdateablePackageList.objects.filter(host_name=host_id).filter(package=x).delete()
        held_packages = centos7_get_locked_packages(ssh)
        UpdateablePackageList.objects.filter(host_addr=host_id).delete()
        centos_update_packages = centos7_get_package_updates(ssh)
        for x in centos_update_packages:
            #print(x)
            for z in centos_update_packages:
                #print(z)
                if x[0] in z:
                    current_package_version = z[2]
            update_package_entry = UpdateablePackageList(host_addr=host_address,package=x[0],currentver=current_package_version,newver=x[2])
            update_package_entry.save()

def hold_packages(host_id, packages_to_hold, TEST_ADDR, TEST_USER, keyfile):
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_address = Hosts.objects.only('hostaddr').get(hostaddr=host_id)
    print(host_address)
    ssh.connect(TEST_ADDR, username=TEST_USER, key_filename=keyfile, timeout=10)
    os_id = os_ident(ssh)
    if 'Ubuntu' in os_id[0]:
        #for x in packages_to_hold:
        #    print(x)
        print("UBUNTU PACKAGES TO HOLD:")
        print(packages_to_hold)
        ubuntu_hold_packages(ssh, packages_to_hold)
        HeldPackageList.objects.filter(host_addr=host_address).delete()
        ubuntu_held_packages = ubuntu_get_held_packages(ssh)
        for x in ubuntu_held_packages:
            print(x)
            held_package_entry = HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1])
            held_package_entry.save()
        #ubuntu_create_host_held_package_table(TEST_DB_HOST, TEST_DB, TEST_USER, TEST_PASS, syshost, held_packages)

    if 'CentOS' in os_id[0]:
        #for x in packages_to_hold:
            #print(x)
        print(type(packages_to_hold))
        centos7_lock_packages(ssh, packages_to_hold)
        HeldPackageList.objects.filter(host_addr=host_address).delete()
        centos_held_packages = centos7_get_locked_packages(ssh)
        for x in centos_held_packages:
            print(x)
            held_package_entry = HeldPackageList(host_addr=host_address,package=x[0],currentver=x[1])
            held_package_entry.save()

def delete_info(scan_address):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Delete existing info - this cascades down to all other linked tables (foreign keys)
    Hosts.objects.filter(hostaddr=scan_address).delete()