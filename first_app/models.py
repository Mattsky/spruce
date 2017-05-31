from django.db import models

# Create your models here.

class Hosts(models.Model):
	id = models.BigAutoField(primary_key=True)
	hostname = models.CharField(max_length=50,unique=True)

	def __str__(self):
		return str(self.hostname)

class HostInfo(models.Model):
	host_name = models.ForeignKey(Hosts)
	host_address = models.CharField(max_length=50)
	os_name = models.CharField(max_length=40)
	os_version = models.CharField(max_length=40)

	def __str__(self):
		return str(self.host_address)

class HeldPackageList(models.Model):
	id = models.BigAutoField(primary_key=True)
	host_name = models.ForeignKey(Hosts)
	package = models.CharField(max_length=40)
	currentver = models.CharField(max_length=40)

	def __str__(self):
		return str(self.package)

class InstalledPackageList(models.Model):
	id = models.BigAutoField(primary_key=True)
	host_name = models.ForeignKey(Hosts)
	package = models.CharField(max_length=60)
	currentver = models.CharField(max_length=60)

	def __str__(self):
		return str(self.package)

class UpdateablePackageList(models.Model):
	id = models.BigAutoField(primary_key=True)
	host_name = models.ForeignKey(Hosts)
	package = models.CharField(max_length=40)
	currentver = models.CharField(max_length=60)
	newver = models.CharField(max_length=60)

	def __str__(self):
		return str(self.package)
