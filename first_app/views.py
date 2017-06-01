from django.shortcuts import render, redirect
from django.conf import settings
import os
from django.http import HttpResponse
from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection
from django.contrib import messages
from first_app.ubuntu_functions import *
from first_app.core_functions import *
from first_app.sql_functions import *
from first_app.centos7_functions import *
import paramiko


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
	
	#host_list = {'hosts':list_of_hosts}
	new_host_list = []
	#print(list_of_hosts)

	#print(list_of_hosts)
	for x in list_of_hosts:
		host_id = Hosts.objects.only('id').get(hostaddr=x)
		host_name = HostInfo.objects.only('host_name').get(host_addr_id=host_id)
		new_host_list.append([x, str(host_name)]) 

	host_list = {'hosts':new_host_list}	

	if request.method == "POST":
		if 'address' in request.POST.keys() and request.POST['address']:
			scan_address = request.POST['address']
		
			rescan(scan_address, TEST_USER, KEYFILE)
			return render(request, 'first_app/index.html', context=host_list)

		if 'delete' in request.POST.keys() and request.POST['delete']:
			scan_address = request.POST['delete']
		
			delete_info(scan_address)
			return render(request, 'first_app/index.html', context=host_list)

	return render(request,'first_app/index.html',context=host_list)

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

		return render(request,'first_app/held.html',context=packageList)

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

		return render(request,'first_app/updates.html',context=updateList)

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
			#TEST_ADDR = syshost
			
			#unhold_packages(host_id, packages_to_unhold, TEST_ADDR, TEST_USER)

		return render(request,'first_app/installed.html',context=packageList)

	except Hosts.DoesNotExist:

		messages.error(request, 'That host does not exist (did you try changing the URL manually?)')
		return redirect('index')

def scan(request):

	try:

		if request.method == "POST":
		
			scan_address = request.POST['address']
			print(scan_address)

			rescan(scan_address, TEST_USER, KEYFILE)
			return render(request, 'first_app/scan.html')

		messages.success(request, 'Scan successful - details added.')
		return render(request,'first_app/scan.html')

	except OSError as e:
		messages.error(request, 'The remote system could not be contacted.')
		return render(request,'first_app/scan.html')
	except NoValidConnectionsError as e:
		messages.error(request, e)
		return render(request,'first_app/scan.html')
