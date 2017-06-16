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

import re, time, datetime
from django.conf import settings
from django.core.files import File
from spruce.subfunctions import *
import os
import io

def get_hostname(ssh):
    try:
        stdin, stdout, stderr = ssh.exec_command('hostname')
        sys_hostname = stdout.read()
        return(sys_hostname)
    except:
        print("ERROR")

def ubuntu_get_package_updates(ssh):
    package_updates = []
    converted_array = []
    stdin, stdout, stderr = ssh.exec_command('sudo apt-get update')
    # Blocking call to wait for updates to be retrieved before running list command
    exit_status = stdout.channel.recv_exit_status()

    stdin, stdout, stderr = ssh.exec_command('sudo apt list --upgradable')
    package_updates = stdout.readlines()
    # Remove header line (cruft)
    del package_updates[0]
    for x in package_updates:
        x = x.rstrip('\n')
        #ssh.close()
        #for x in package_updates:
        package_name_temp = re.search(r'^(.+?)/', x)
        package_name = package_name_temp.group(1)
        package_new_ver_temp = re.search(r' (.+?) ', x)
        package_new_ver = package_new_ver_temp.group(1)
        package_current_ver_temp = re.search(r'upgradable from: (.+?)]', x)
        package_current_ver = package_current_ver_temp.group(1)
        y = [package_name, package_current_ver, package_new_ver]
        converted_array.append(y)
    return(converted_array)

def ubuntu_get_held_packages(ssh):
    held_packages = []
    package_info = []
    stdin, stdout, stderr = ssh.exec_command('sudo apt-mark showhold')
    #stdin, stdout, stderr = ssh.exec_command('sudo dpkg -l | grep "^hi"')
    held_packages = stdout.readlines()
    for x in held_packages:
        x = x.rstrip('\n')
        stdin, stdout, stderr = ssh.exec_command('sudo apt list ' + x )
        heldpackageinfo = stdout.readlines()
        #Get rid of 'Listing...' entry
        heldpackageinfo = heldpackageinfo[1:]
        for z in heldpackageinfo:
            package_name = str.split(z)[0]
            package_ver = str.split(z)[1]
            package_info.append([package_name, package_ver])
    return(package_info)



def ubuntu_get_all_installed_packages(ssh):
    
    package_array = []
    converted_package_array = []
    stdin, stdout, stderr = ssh.exec_command('sudo apt list --installed > /tmp/pkglist')
    exit_status = stdout.channel.recv_exit_status()
    sftp = ssh.open_sftp()
    sftp.get('/tmp/pkglist', '/tmp/pkglist_test')
    sftp.close()
    
    packagefile = open('/tmp/pkglist_test')
    packagelist = packagefile.readlines()[1:]
    for line in packagelist:
        package_name_temp = re.search(r'^(.+?)/', line)
        package_name = package_name_temp.group(1)
        package_version_temp = re.search(r' (.+?) ', line)
        package_version = package_version_temp.group(1)
        y = [ package_name, package_version ]
        converted_package_array.append(y)
    return(converted_package_array)


    
def ubuntu_hold_packages(ssh, packagelist):
    
    try:
        log_dir = settings.LOG_DIR
        package_list_string = ""
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")
        package_list_string = ""

        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark hold ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "hold"
            log_write(packagelist, host_name, action_type)

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark hold ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "hold"
            log_write(packagelist, host_name, action_type)
  
        return("SUCCESS")
    except:
        return("FAILURE")

def ubuntu_unhold_packages(ssh, packagelist):
    
    try:
        log_dir = settings.LOG_DIR
        package_list_string = ""
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")
        package_list_string = ""
        print(type(packagelist))
        if isinstance(packagelist, list):
            print("UBUNTU UNHOLD LIST")
            for x in packagelist:
                normal_package_name = x.split('/')[0]
                package_list_string = package_list_string + normal_package_name + ' '
            print("PACKAGE LIST: "+package_list_string)
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark unhold ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "unhold"
            log_write(packagelist, host_name, action_type)

        elif isinstance(packagelist, str):
            print("UBUNTU UNHOLD STRING")
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark unhold ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "unhold"
            log_write(packagelist, host_name, action_type)
 
        return("SUCCESS")
    except:
        return("FAILURE")

def ubuntu_apply_package_updates(ssh, packagelist):
    
    try:
        log_dir = settings.LOG_DIR
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")
        print(type(packagelist))
        complete_packagelist = ""
        final_packagelist = []
        if isinstance(packagelist, list):
            print(packagelist)
            for x in packagelist:
                print(x)
                print('package name: ' + x)
                # Add space for building total package list ("packagename " - "package1package2" will break it)
                complete_packagelist = complete_packagelist + (x + ' ')
            print("Installing: " + complete_packagelist)
            stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y install --only-upgrade ' + complete_packagelist)
            stdout = stdout.readlines()
            #for line in stdout:
                #print(line)
            action_type = "update"

            log_write(packagelist, host_name, action_type)
            

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y install --only-upgrade ' + x)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "update"

            log_write(packagelist, host_name, action_type)

        print("SUCCESS")
    except:
        print("FAILURE")
    
def ubuntu_list_package_updates(ssh, date):

    try:
        total_package_list = ""
        stdin, stdout, stderr = ssh.exec_command("sudo grep -A 1 'Start-Date: " + date + "' /var/log/apt/history.log")
        stdout = stdout.readlines()
        for line in stdout:
            #print(line)  
            if "Commandline" in line:
                line = line.rstrip()
                #print(line)
                packages_temp = re.search(r'^Commandline: apt-get -y install --only-upgrade (.+?)$', line)
                if packages_temp:
                    packages = packages_temp.group(1)
                    packages = packages + ' '
                    total_package_list = total_package_list + packages

        print(total_package_list)
        print("SUCCESS")
    except:
        print("FAILURE")

def ubuntu_install_specific_version_package(ssh, package, version):
    
    try:
        stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y install ' + package + '=' + version)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        for line in stdout:
            print(line)
        for line in stderr:
            print(line)

        log_write(package, host_name, action_type)

        print("SUCCESS")
    except:
        print("FAILURE")

def ubuntu_get_update_history(ssh):
    converted_output_array = []
    stdin, stdout, stderr = ssh.exec_command('zcat /var/log/apt/history.log.*.gz | grep -a --text -i upgrade | grep -vi commandline | grep -vi install')
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.readlines()
    count = 1
    for line in output:
        line = line[9:]
        line = line.rstrip()
        sub_list = line.split("),")
        for x in sub_list:
            x = x.replace(",","")
            x = x.replace("(","")
            x = x.replace(")","")
            x = x.lstrip()
            package_info_list = x.split(" ")
            converted_output_array.append(str(count) + ' | ' + package_info_list[0] + ' | ' + package_info_list[1] + ' | ' + package_info_list[2])
            count+=1
    #    converted_output_array.append[line]
    converted_output_array.insert(0,"ID | Package | Previous Version | Updated Version")
    return(converted_output_array)

def ubuntu_roll_back_update(ssh, transact_id):
    try:
        update_history_list = ubuntu_get_update_history(ssh)
        target_update = update_history_list[int(transact_id)]
        print(target_update[1])
        print(target_update[2])
        pkgname = target_update[1].split(":")[0]
        print(pkgname)
        commandstring = 'sudo apt-get -y --allow-downgrades -o Dpkg::Options::="--force-confold" --force-yes install ' + pkgname + '=' + target_update[2]
        print(commandstring)
        stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y --allow-downgrades -o Dpkg::Options::="--force-confold" --force-yes install ' + pkgname + '=' + target_update[2])
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read()
        error_msg = stderr.read()
        if(error_msg):
            return("An error occurred. Please check the transaction ID and the system log if issues persist.")
        elif(output):
            return("Operation successful.")

    except:
        print("PROBLEM!")
