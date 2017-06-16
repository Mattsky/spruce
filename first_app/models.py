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

from django.db import models

# Create your models here.

class Hosts(models.Model):
    hostaddr = models.CharField(max_length=50,unique=True)
    hostport = models.CharField(max_length=5)

    def __str__(self):
        return str(self.hostaddr)

class HostInfo(models.Model):
    host_addr = models.ForeignKey(Hosts)
    host_name = models.CharField(max_length=50)
    os_name = models.CharField(max_length=40)
    os_version = models.CharField(max_length=40)

    def __str__(self):
        return str(self.host_name)

class HeldPackageList(models.Model):
    id = models.BigAutoField(primary_key=True)
    host_addr = models.ForeignKey(Hosts)
    package = models.CharField(max_length=40)
    currentver = models.CharField(max_length=40)

    def __str__(self):
        return str(self.package)

class InstalledPackageList(models.Model):
    id = models.BigAutoField(primary_key=True)
    host_addr = models.ForeignKey(Hosts)
    package = models.CharField(max_length=60)
    currentver = models.CharField(max_length=60)

    def __str__(self):
        return str(self.package)

class UpdateablePackageList(models.Model):
    id = models.BigAutoField(primary_key=True)
    host_addr = models.ForeignKey(Hosts)
    package = models.CharField(max_length=40)
    currentver = models.CharField(max_length=60)
    newver = models.CharField(max_length=60)

    def __str__(self):
        return str(self.package)
