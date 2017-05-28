import re, time

def centos7_get_package_updates(ssh):
    package_updates = []
    filtered_package_updates = []
    #ssh.exec_command('sudo apt-get update')
    stdin, stdout, stderr = ssh.exec_command('sudo yum check-updates')
    package_updates = stdout.readlines()
    # Remove header lines (cruft)
    
    print(type(package_updates))
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
            package_name = package_info.split('-')[0]
            package_version = package_info.split('-',1)[1]

            locked_package_info.append([package_name, package_version])
    # Return alphabetically sorted list of packages
    return(sorted(locked_package_info))

def centos7_lock_packages(ssh, packagelist):
    
    try:
        print(type(packagelist))
        package_list_string = ""
        # isinstance list check may need changing to tuple when results pulled from DB
        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()
        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()

        return("SUCCESS")
    except:
        return("FAILURE")

def centos7_unlock_packages(ssh, packagelist):
    
    try:
        print(type(packagelist))
        package_list_string = ""
        # isinstance list check may need changing to tuple when results pulled from DB
        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock delete ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()
        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum versionlock delete ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()
  
        return("SUCCESS")
    except:
        return("FAILURE")

def centos7_update_packages(ssh, packagelist):
    
    try:
        print(type(packagelist))
        package_list_string = ""
        # isinstance list check may need changing to tuple when results pulled from DB
        if isinstance(packagelist, list):
            for x in packagelist:
                package_list_string = package_list_string + x + ' '
            stdin, stdout, stderr = ssh.exec_command('sudo yum -y update ' + package_list_string)
            exit_status = stdout.channel.recv_exit_status()
        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo yum -y update ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()
  
        return("SUCCESS")
    except:
        return("FAILURE")