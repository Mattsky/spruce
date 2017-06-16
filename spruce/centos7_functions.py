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

def get_hostname(ssh):
    try:
        stdin, stdout, stderr = ssh.exec_command('hostname')
        sys_hostname = stdout.read()
        return(sys_hostname)
    except:
        print("ERROR")

def centos7_get_package_updates(ssh):
    package_updates = []
    filtered_package_updates = []
    #ssh.exec_command('sudo apt-get update')
    stdin, stdout, stderr = ssh.exec_command('sudo yum check-updates')
    package_updates = stdout.readlines()
    # Remove header lines (cruft)
    
    arch_to_check = ['x86_64','noarch']
    for line in package_updates:
        if any(x in line for x in arch_to_check):
            line = line.rstrip('\n')
            

            package_name = str.split(line)[0]
            package_version = str.split(line)[1]
            package_repo = str.split(line)[2]

            # Further split package info into name and architecture - output is <name>.<arch>
            package_info = package_name.split('.')
            # Structure: package name, arch, update version, repo
            y = [ package_info[0], package_info[1], package_version, package_repo ]
            filtered_package_updates.append(y)
            
    return(filtered_package_updates)

def centos7_get_all_installed_packages(ssh):
    # yum-plugin-versionlock.noarch         1.1.31-40.el7                    @base
    package_array = []
    filtered_package_array = []
    stdin, stdout, stderr = ssh.exec_command('sudo yum list installed')
    package_array = stdout.readlines()
    # Remove unneeded lines from output - only keep stuff with specific architecture info
    arch_to_check = ['x86_64','noarch']
    for line in package_array:
        if any(x in line for x in arch_to_check): 
            #print(line)   
            package_name = str.split(line)[0]
            package_version = str.split(line)[1]

            # Further split package info into name and architecture - output is <name>.<arch>
        
            package_info = package_name.split('.')
            # Structure: package name, arch, current version
            y = [ package_info[0], package_info[1], package_version ]
            filtered_package_array.append(y)
    return(filtered_package_array)

def centos7_get_locked_packages(ssh):
    locked_packages = []
    locked_package_info = []
    # Exclude nonessential info lines from list to be parsed
    text_to_check = ['list done','Loaded']
    stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock')
    held_packages = stdout.readlines()
    for line in held_packages:
        if not any(x in line for x in text_to_check): 
            line = line.rstrip('\n')
            # Strip leading "0:" bit...
            package_info = line.split(':')[1]
            # ...then strip the trailing ".*"...
            package_info = package_info.split('.*')[0]
            # ...and finally split the remainder into package name and version.
            #package_name = package_info.split('-')[0]
            #package_version = package_info.split('-',1)[1]
            package_name = re.split('(\d.*)', package_info)[0]
            package_name = package_name[:-1]
            package_version = re.split('(\d.*)', package_info)[1]
            locked_package_info.append([package_name, package_version])
    # Return alphabetically sorted list of packages
    return(sorted(locked_package_info))

def centos7_lock_packages(ssh, packagelist):
    
    try:
        print("HELLO")
        log_dir = settings.LOG_DIR
        print("LOGDIR SET")
        package_list_string = ""
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")
        print(host_name)
        print(type(packagelist))
        package_list_string = ""
        print(packagelist)
        #print("LOCK_PACKAGE_FUNCTION_PACKAGELIST: " + type(packagelist))
        
        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "hold"
            log_write(packagelist, host_name, action_type)

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "hold"
            log_write(packagelist, host_name, action_type)

        return("SUCCESS")
    except:
        print("FAILURE TO LOCK")

def centos7_unlock_packages(ssh, packagelist):
    
    try:

        log_dir = settings.LOG_DIR
        package_list_string = ""
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")

        package_list_string = ""
        # isinstance list check may need changing to tuple when results pulled from DB
        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock delete ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()
      
            action_type = "unhold"
            log_write(packagelist, host_name, action_type)

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock delete ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()
    
            action_type = "unhold"
            log_write(packagelist, host_name, action_type)

        return("SUCCESS")
    except:
        return("FAILURE")

def centos7_update_packages(ssh, packagelist):
    
    try:
        
        log_dir = settings.LOG_DIR
        package_list_string = ""
        host_name = get_hostname(ssh)
        #Strip whitespace from end of hostname
        host_name = host_name.rstrip()
        # Convert hostname from bytes to usable string
        host_name = host_name.decode("utf-8")

        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum -y update ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "update"
            print(action_type)
            log_write(packagelist, host_name, action_type)

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum -y update ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()

            action_type = "update"
            log_write(packagelist, host_name, action_type)

        return("SUCCESS")
    except:
        print("FAILURE")

def centos_get_update_history(ssh):
    stdin, stdout, stderr = ssh.exec_command('sudo yum history')
    converted_output = []
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.readlines()
    for line in output:
        line = line.rstrip()
        converted_output.append(line)
    return(converted_output)

def centos7_roll_back_update(ssh, transact_id):
    try:
        stdin, stdout, stderr = ssh.exec_command('sudo yum -y history undo ' + str(transact_id))
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read()
        error_msg = stderr.read()
        if(error_msg):
            return("An error occurred. Please check the transaction ID and the system log if issues persist.")
        elif(output):
            return("Operation successful.")

    except:
        print("PROBLEM!")
