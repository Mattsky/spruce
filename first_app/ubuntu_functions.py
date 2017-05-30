import re, time

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
        package_current_ver_temp = re.search(r' (.+?) ', x)
        package_current_ver = package_current_ver_temp.group(1)
        package_new_ver_temp = re.search(r'upgradable from: (.+?)]', x)
        package_new_ver = package_new_ver_temp.group(1)
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
        print("WHOLE THING: "+str(heldpackageinfo))
        #Get rid of 'Listing...' entry
        heldpackageinfo = heldpackageinfo[1:]
        for z in heldpackageinfo:
            print("HELD PACKAGE: "+ z )
            package_name = str.split(z)[0]
            print(package_name)
            package_ver = str.split(z)[1]
            print(package_ver)
            package_info.append([package_name, package_ver])
    return(package_info)

def ubuntu_get_all_installed_packages(ssh):
    # zssh/xenial 1.5c.debian.1-3.2 amd64
    package_array = []
    converted_package_array = []
    stdin, stdout, stderr = ssh.exec_command('sudo apt list')
    package_array = stdout.readlines()
    # Remove 'listing' entry
    del package_array[0]
    for x in package_array:
        package_name_temp = re.search(r'^(.+?)/', x)
        package_name = package_name_temp.group(1)
        package_version_temp = re.search(r' (.+?) ', x)
        package_version = package_version_temp.group(1)
        y = [ package_name, package_version ]
        converted_package_array.append(y)
    return(converted_package_array)

# EXPERIMENTAL CODE TO RETRIEVE LIST OF FILES IN A... FILE AS OPPOSED TO SSH

def ubuntu_get_all_installed_packages_new(ssh):
    # zssh/xenial 1.5c.debian.1-3.2 amd64
    package_array = []
    converted_package_array = []
    stdin, stdout, stderr = ssh.exec_command('sudo apt list > /tmp/pkglist')
    exit_status = stdout.channel.recv_exit_status()
    sftp = ssh.open_sftp()
    sftp.get('/tmp/pkglist', '/tmp/pkglist_test')
    sftp.close()
    #for line in remote_packagelist_file:
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

# END EXPERIMENTAL CODE
    
def ubuntu_hold_packages(ssh, packagelist):
    
    try:
        print(type(packagelist))
        if isinstance(packagelist, list):
            for x in packagelist:
                stdin, stdout, stderr = ssh.exec_command('sudo apt-mark hold ' + x)
                exit_status = stdout.channel.recv_exit_status()
        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark hold ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()
  
        return("SUCCESS")
    except:
        return("FAILURE")

def ubuntu_unhold_packages(ssh, packagelist):
    
    try:
        print(type(packagelist))
        if isinstance(packagelist, list):
            for x in packagelist:
                stdin, stdout, stderr = ssh.exec_command('sudo apt-mark unhold ' + x)
                exit_status = stdout.channel.recv_exit_status()
        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo apt-mark unhold ' + packagelist)
            exit_status = stdout.channel.recv_exit_status()
 
        return("SUCCESS")
    except:
        return("FAILURE")

def ubuntu_apply_package_updates(ssh, packagelist):
    
    try:
        print(type(packagelist))
        complete_packagelist = ""
        if isinstance(packagelist, tuple):
            for x in packagelist:
                print(x)
                print('package name: ' + str(x))
                # Convert tuple object to string, then strip off leading "('" and trailing "',)"
                packagename = str(x)
                packagename = packagename[:-3]
                packagename = packagename[2:]
                # Add space for building total package list ("packagename " - "package1package2" will break it)
                print('new package name: ' + packagename)
                complete_packagelist = complete_packagelist + (packagename + ' ')
            print("Installing: " + complete_packagelist)
            stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y install --only-upgrade ' + complete_packagelist)
            stdout = stdout.readlines()
            for line in stdout:
                print(line)
            

        elif isinstance(packagelist, str):
            stdin, stdout, stderr = ssh.exec_command('sudo apt-get -y install --only-upgrade ' + x)
    

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

        print("SUCCESS")
    except:
        print("FAILURE")