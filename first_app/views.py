from django.shortcuts import render
from django.http import HttpResponse
from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList, Hosts, HostInfo
from django.db import connection
from first_app.ubuntu_functions import *
from first_app.core_functions import *
from first_app.sql_functions import *
from first_app.centos7_functions import *
import paramiko


#TEST_ADDR = '192.168.0.22'
TEST_DB_HOST = '192.168.0.22'
TEST_USER = 'matt'
TEST_PASS = 'password'
TEST_DB = 'testdb'


# Create your views here.

def index(request):
	
	list_of_hosts = Hosts.objects.values_list('hostname', flat=True)
	# Test code to only keep tables with 'held' in the name
	#list_of_tables = [x for x in tables if 'held' in x]
				
	host_list = {'hosts':list_of_hosts}

	if request.method == "POST":
		scan_address = request.POST['address']
		rescan_test(scan_address, TEST_USER)
		return render(request, 'first_app/index.html', context=host_list)

	return render(request,'first_app/index.html',context=host_list)

	#webpages_list = AccessRecord.objects.order_by('date')
	#date_dict = {'access_records':webpages_list}
	#return render(request,'first_app/index.html',context=date_dict)

def held(request):
	syshost = request.GET['hostname']
	# Get matching host ID from Hosts model for further ops	
	host_id = Hosts.objects.only('id').get(hostname=syshost)
	heldpackages = HeldPackageList.objects.filter(host_name=host_id)
	packageList = {'heldpackages': heldpackages}
	
	if request.method == 'POST':
		TEST_ADDR = syshost
		ssh = paramiko.SSHClient()

		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		ssh.connect(TEST_ADDR, username=TEST_USER, key_filename='/home/matt/.ssh/id_rsa', timeout=10)
		os_id = os_ident(ssh)
		if 'Ubuntu' in os_id[0]:
			packages_to_unhold = request.POST.getlist('package')
			for x in packages_to_unhold:
				print(x)
				ubuntu_unhold_packages(ssh, x)
				HeldPackageList.objects.filter(host_name=host_id).filter(package=x).delete()
			held_packages = ubuntu_get_held_packages(ssh)
			#ubuntu_create_host_held_package_table(TEST_DB_HOST, TEST_DB, TEST_USER, TEST_PASS, syshost, held_packages)

		if 'CentOS' in os_id[0]:
			packages_to_unhold = request.POST.getlist('package')
			for x in packages_to_unhold:
				print(x)
				centos7_unlock_packages(ssh, x)
				HeldPackageList.objects.filter(host_name=host_id).filter(package=x).delete()
			held_packages = centos7_get_locked_packages(ssh)


	return render(request,'first_app/held.html',context=packageList)

def updates(request):
	syshost = request.GET['hostname']
	# Get matching host ID from Hosts model for further ops
	host_id = Hosts.objects.only('id').get(hostname=syshost)
	availableupdates = UpdateablePackageList.objects.filter(host_name=host_id)
	updateList = {'availableupdates': availableupdates}
	return render(request,'first_app/updates.html',context=updateList)

def installed(request):
	syshost = request.GET['hostname']
	# Get matching host ID from Hosts model for further ops
	host_id = Hosts.objects.only('id').get(hostname=syshost)
	installedpackages = InstalledPackageList.objects.filter(host_name=host_id)
	packageList = {'installedpackages': installedpackages}
	return render(request,'first_app/installed.html',context=packageList)

def scan(request):

	if request.method == "POST":
		scan_address = request.POST['address']
		print(scan_address)

		rescan_test(scan_address, TEST_USER)
		return render(request, 'first_app/scan.html')


	return render(request,'first_app/scan.html')
