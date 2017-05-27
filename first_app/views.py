from django.shortcuts import render
from django.http import HttpResponse
from first_app.models import UpdateablePackageList, InstalledPackageList, HeldPackageList
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
	tables = connection.introspection.table_names()

	list_of_tables = []
	# Test code to only keep tables with 'held' in the name
	#list_of_tables = [x for x in tables if 'held' in x]

	target_strings = ("held", "update", "packages")
	for x in tables:
		if any(s in x for s in target_strings):
			if 'first_app' not in x:
				list_of_tables.append(x)	
				
	table_list = {'tables':list_of_tables}
	return render(request,'first_app/index.html',context=table_list)

	#webpages_list = AccessRecord.objects.order_by('date')
	#date_dict = {'access_records':webpages_list}
	#return render(request,'first_app/index.html',context=date_dict)

def held(request):
	syshost = request.GET['hostname']
	#packagequery = '''SELECT id, package, currentver from `'''+ syshost +'''_held`'''
	#heldpackages = HeldPackageList.objects.raw(packagequery)
	#Original working hardcoded line below
	heldpackages = HeldPackageList.objects.raw('''SELECT id, package, currentver from `''' + syshost + '''_held`''')
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
	availableupdates = UpdateablePackageList.objects.raw('''SELECT id, package, currentver, newver from `''' + syshost + '''_updates`''')
	updateList = {'availableupdates': availableupdates}
	return render(request,'first_app/updates.html',context=updateList)

def installed(request):
	syshost = request.GET['hostname']
	installedpackages = InstalledPackageList.objects.raw('''SELECT id, package, currentver from `''' + syshost + '''_packages`''')
	packageList = {'installedpackages': installedpackages}
	return render(request,'first_app/installed.html',context=packageList)
