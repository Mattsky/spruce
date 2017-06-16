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

from django.shortcuts import render, redirect
from django.conf import settings
import os
from django.http import HttpResponse
from spruce.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection
from django.contrib import messages
from spruce.ubuntu_functions import *
from spruce.core_functions import *
from spruce.sql_functions import *
from spruce.centos7_functions import *
from spruce.subfunctions import *
import paramiko
import re, time, datetime
#from django.views.generic.base import TemplateView

#TEST_ADDR = '192.168.0.22'
#TEST_DB_HOST = '172.19.8.70' #OSX lab server
#TEST_DB_HOST = '192.168.0.22' #Home lab DB server
TEST_DB_HOST = settings.DATABASES['default']['HOST']
TEST_USER = 'matt'
TEST_PASS = 'password'
TEST_DB = 'testdb'
HOMEDIR = os.path.expanduser('~')
KEYFILE = HOMEDIR + '/.ssh/id_rsa'

# Create your views here.

def index(request):
    
    list_of_hosts = Hosts.objects.values_list('hostaddr', flat=True)
    
    new_host_list = []
    
    for x in list_of_hosts:
        host_id = Hosts.objects.only('id').get(hostaddr=x)
        host_port = Hosts.objects.filter(hostaddr=x).values_list('hostport', flat=True)
        
        host_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('host_name', flat=True)
        
        os_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_name', flat=True)
        os_version = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_version', flat=True)

        new_host_list.append([x, str(host_name[0]), str(os_name[0]), str(os_version[0]), str(host_port[0])]) 

    
    host_list = {'hosts':new_host_list} 

    if request.method == "POST":
        if 'address' in request.POST.keys() and request.POST['address']:
            target_address = request.POST['address']
            scan_address = target_address.split(':')[0]
            scan_port_temp = target_address.split(':')[1]
            scan_port = scan_port_temp.split('}')[0]
            print(scan_address)
            print(scan_port)
            
            rescan(scan_address, scan_port, TEST_USER, KEYFILE)
            list_of_hosts = Hosts.objects.values_list('hostaddr', flat=True)
    
            new_host_list = []

            for x in list_of_hosts:
                host_id = Hosts.objects.only('id').get(hostaddr=x)
                host_port = Hosts.objects.filter(hostaddr=x).values_list('hostport', flat=True)
                host_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('host_name', flat=True)
                os_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_name', flat=True)
                os_version = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_version', flat=True)

                new_host_list.append([x, str(host_name[0]), str(os_name[0]), str(os_version[0]), str(host_port[0])]) 

            host_list = {'hosts':new_host_list} 
            return render(request, 'spruce/index.html', context=host_list)

        if 'delete' in request.POST.keys() and request.POST['delete']:
            scan_address = request.POST['delete']
        
            delete_info(scan_address)
            list_of_hosts = Hosts.objects.values_list('hostaddr', flat=True)
    
            new_host_list = []
            
            for x in list_of_hosts:
                host_id = Hosts.objects.only('id').get(hostaddr=x)
                host_port = Hosts.objects.filter(hostaddr=x).values_list('hostport', flat=True)
                host_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('host_name', flat=True)
                os_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_name', flat=True)
                os_version = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_version', flat=True)

                new_host_list.append([x, str(host_name[0]), str(os_name[0]), str(os_version[0]), str(host_port[0])]) 

            host_list = {'hosts':new_host_list} 
            return render(request, 'spruce/index.html', context=host_list)

        if 'scan_all' in request.POST.keys() and request.POST['scan_all']:
            
            list_of_scan_targets = []
            list_of_addresses = Hosts.objects.values_list('hostaddr', flat=True)
            list_of_ports = Hosts.objects.values_list('hostport', flat=True)
            for x in range(0, len(list_of_addresses)):
                #list_of_hosts.append([ list_of_addresses[x] , list_of_ports[x] ])
                print(list_of_addresses[x])
                print(list_of_ports[x])
                list_of_scan_targets.append([list_of_addresses[x], list_of_ports[x]])
            print(list_of_scan_targets)

            multi_system_rescan(list_of_scan_targets, TEST_USER, KEYFILE)

            new_host_list = []
            
            for x in list_of_hosts:
                host_id = Hosts.objects.only('id').get(hostaddr=x)
                host_port = Hosts.objects.filter(hostaddr=x).values_list('hostport', flat=True)
                host_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('host_name', flat=True)
                os_name = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_name', flat=True)
                os_version = HostInfo.objects.filter(host_addr_id=host_id).values_list('os_version', flat=True)

                new_host_list.append([x, str(host_name[0]), str(os_name[0]), str(os_version[0]), str(host_port[0])]) 

            host_list = {'hosts':new_host_list} 
            return render(request, 'spruce/index.html', context=host_list)


    return render(request,'spruce/index.html',context=host_list)

def held(request):
    
    try:

        syshost = request.GET['hostaddr']
        # Get matching host ID from Hosts model for further ops 
        host_id = Hosts.objects.only('id').get(hostaddr=syshost)
        heldpackages = HeldPackageList.objects.filter(host_addr=host_id)
        packageList = {'heldpackages': heldpackages}
        
        if request.method == 'POST':
            packages_to_unhold = request.POST.getlist('package')
            TEST_ADDR = syshost
            
            unhold_packages(host_id, packages_to_unhold, TEST_ADDR, TEST_USER, KEYFILE)

        return render(request,'spruce/held.html',context=packageList)

    except Hosts.DoesNotExist:

        messages.error(request, 'That host does not exist (did you try changing the URL manually?)')
        return redirect('index')


def updates(request):

    try:

        syshost = request.GET['hostaddr']
        # Get matching host ID from Hosts model for further ops
        host_id = Hosts.objects.only('id').get(hostaddr=syshost)
        availableupdates = UpdateablePackageList.objects.filter(host_addr=host_id)
        updateList = {'availableupdates': availableupdates}

        if request.method == 'POST':
            packages_to_update = request.POST.getlist('package')
            TEST_ADDR = syshost
            
            update_packages(host_id, packages_to_update, TEST_ADDR, TEST_USER, KEYFILE)

        return render(request,'spruce/updates.html',context=updateList)

    except Hosts.DoesNotExist:

        messages.error(request, 'That host does not exist (did you try changing the URL manually?)')
        return redirect('index')

def installed(request):

    try:

        syshost = request.GET['hostaddr']
        # Get matching host ID from Hosts model for further ops
        host_id = Hosts.objects.only('id').get(hostaddr=syshost)
        installedpackages = InstalledPackageList.objects.filter(host_addr=host_id)
        packageList = {'installedpackages': installedpackages}

        if request.method == 'POST':
            packages_to_lock = request.POST.getlist('package')
            TEST_ADDR = syshost
            for x in packages_to_lock:
                print(x)
            hold_packages(host_id, packages_to_lock, TEST_ADDR, TEST_USER, KEYFILE)

        return render(request,'spruce/installed.html',context=packageList)

    except Hosts.DoesNotExist:

        messages.error(request, 'That host does not exist (did you try changing the URL manually?)')
        return redirect('index')

def scan(request):

    try:

        if request.method == "POST":
            if 'address' in request.POST.keys() and request.POST['address']:
                if 'sshport' not in request.POST:
                    scan_port = '22'
                else:
                    scan_port = request.POST['sshport']
                scan_address = request.POST['address']
                rescan(scan_address, scan_port, TEST_USER, KEYFILE)
                messages.success(request, 'Scan successful - details added.')
                return render(request, 'spruce/scan.html')

            
        return render(request,'spruce/scan.html')

    except OSError as e:
        messages.error(request, 'The remote system could not be contacted.')
        return render(request,'spruce/scan.html')
    except NoValidConnectionsError as e:
        messages.error(request, e)
        return render(request,'spruce/scan.html')

def update_history(request):

    try:

        target_address = request.GET['hostaddr']
        output = get_update_history(target_address, TEST_USER, KEYFILE)
        if request.method == "POST":
            target_address = request.GET['hostaddr']
            output = get_update_history(target_address, TEST_USER, KEYFILE)
            if 'input_id' in request.POST.keys() and request.POST['input_id']:
                transact_id = request.POST['input_id']
                
                status_message = rollback_update(transact_id, target_address, TEST_USER, KEYFILE)
                messages.info(request, status_message)
                output = get_update_history(target_address, TEST_USER, KEYFILE)

        return render(request, 'spruce/history.html', {'output': output})

    except:
        print("OHNOES")


def upload_file(request):
    
    try:
        if request.method == "POST":
            system_list = []
            f = request.FILES['hostFile'] # Grab uploaded file for parsing
            for line in f:
                teststring = line.decode("utf-8")

                # Convert bytes literal to string so we can breathe easier..
                # Check line isn't a section header
                if '[' not in teststring:
                    # Check line isn't totally empty
                    if teststring !='\r\n':
                        print(teststring)        
                        #host_address=line.decode("utf-8").split('=')[1]
                        if "host" in teststring:
                            ip_address_temp = re.search(r'ansible_host=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', teststring)
                            ip_address = ip_address_temp.group(1)
                        
                        if "port" in teststring:
                            print("YAY")
                            connect_port_temp = re.search(r'ansible_port=(\d+)', teststring)
                            connect_port = connect_port_temp.group(1)
                            print("PORT FOUND IN FILE")
                            print(connect_port)
                        else:
                            connect_port=22
                            print(connect_port)
                        
                        system_list.append([ip_address, str(connect_port)])
            print(system_list)

            
            multi_system_scan(system_list, TEST_USER, KEYFILE)
            messages.success(request, 'All systems were scanned. Please check the index.')
        return render(request, 'spruce/upload_inventory.html')
    except:
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'spruce/upload_inventory.html')