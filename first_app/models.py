from django.db import models

# Create your models here.

class HeldPackageList(models.Model):
	package = models.CharField(max_length=40)
	currentver = models.CharField(max_length=40)

	def __str__(self):
		return str(self.package)

class InstalledPackageList(models.Model):
	package = models.CharField(max_length=60)
	currentver = models.CharField(max_length=60)

	def __str__(self):
		return str(self.package)

class UpdateablePackageList(models.Model):
	package = models.CharField(max_length=40)
	currentver = models.CharField(max_length=60)
	newver = models.CharField(max_length=60)

	def __str__(self):
		return str(self.package)
