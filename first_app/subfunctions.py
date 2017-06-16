from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection, transaction
from django.conf import settings
from django.core.files import File
import re, time, datetime, os

def log_write(packagelist, host_name, action_type):
    try:

        log_dir = settings.LOG_DIR
        if isinstance(packagelist, list):

            timestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.now())
            print(log_dir)
            print(host_name)
            print(timestamp)
            
            logfile_target = os.path.join(log_dir,host_name + '_' + action_type + '-' + timestamp + '.txt')
            print(logfile_target)
            logfile = open(logfile_target, 'w')
            if action_type=="update":
                logfile.write("The below packages were updated:\n")
            elif action_type=="unhold":
                logfile.write("The below packages were unlocked:\n")
            elif action_type=="hold":
                logfile.write("The below packages were locked:\n")

            for item in packagelist:
                print(item)
                logfile.write("%s\n" % item)
            logfile.close()

        elif isinstance(packagelist, str):

            timestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.now())
            print(log_dir)
            print(type(host_name))
            print(str(host_name))
            print(timestamp)
            logfile_target = os.path.join(log_dir,host_name + '_' + action_type + '-' + timestamp + '.txt')
            print(logfile_target)
            logfile = open(logfile_target, 'w')
            if action_type=="update":
                logfile.write("The below packages were updated:\n")
            elif action_type=="unhold":
                logfile.write("The below packages were unlocked:\n")
            elif action_type=="hold":
                logfile.write("The below packages were locked:\n")
            logfile.write("%s\n" % packagelist)
            logfile.close()
    except:

        print("FAILURE WRITING LOGS")
