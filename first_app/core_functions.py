import paramiko

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
                    return(OS + ' ' + Version)
                
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
                    return(OS + ' ' + Version)

        except IOError:
            print("File not found!")

    except paramiko.SSHException:
        print("Connection error")