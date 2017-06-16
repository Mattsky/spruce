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

from django.contrib import admin
from spruce.models import Hosts, HostInfo, HeldPackageList, InstalledPackageList, UpdateablePackageList

# Register your models here.
admin.site.register(Hosts)
admin.site.register(HostInfo)
admin.site.register(HeldPackageList)
admin.site.register(InstalledPackageList)
admin.site.register(UpdateablePackageList)
