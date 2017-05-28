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

		packages_to_unhold = request.POST.getlist('package')
		for x in packages_to_unhold:
			print(x)
			ubuntu_unhold_packages(ssh, x)
		held_packages = ubuntu_get_held_packages(ssh)
		ubuntu_create_host_held_package_table(TEST_DB_HOST, TEST_DB, TEST_USER, TEST_PASS, syshost, held_packages)


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
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		# Delete existing info prior to refresh and recreate, just in case
		Hosts.objects.filter(hostname=scan_address).delete()
		host_entry = Hosts(hostname=scan_address)
		host_entry.save()

		ssh.connect(scan_address, username=TEST_USER, key_filename='/home/matt/.ssh/id_rsa', timeout=10)
		os_id = os_ident(ssh)
		print(os_id)
		
		host_address = Hosts.objects.only('hostname').get(hostname=scan_address)
		#FIX THIS BIT - REARRANGE MODELS AS REQUIRED!
		host_name = get_hostname(ssh)
		#Strip whitespace from end of hostname
		host_name = host_name.rstrip()
		host_info_entry = HostInfo(host_name=host_address, host_address=host_name, os_name=os_id[0], os_version=os_id[1])
		host_info_entry.save()
				
		if 'CentOS' in os_id[0]:
			centos_installed_packages = centos7_get_all_installed_packages(ssh)
			for x in centos_installed_packages:
				print(x)
				installed_package_entry = InstalledPackageList(host_name=host_address, package=x[0], currentver=x[2])
				installed_package_entry.save()
			centos_held_packages = centos7_get_locked_packages(ssh)
			for x in centos_held_packages:
				print(x)
				held_package_entry = HeldPackageList(host_name=host_address,package=x[0],currentver=x[1])
				held_package_entry.save()
			centos_update_packages = centos7_get_package_updates(ssh)
			for x in centos_update_packages:
				print(x)
				for z in centos_installed_packages:
					print(z)
					if x[0] in z:
						current_package_version = z[2]
				update_package_entry = UpdateablePackageList(host_name=host_address,package=x[0],currentver=current_package_version,newver=x[2])
				update_package_entry.save()


	return render(request,'first_app/scan.html')
