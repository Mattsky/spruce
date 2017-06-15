from django.contrib import admin
from first_app.models import Hosts, HostInfo, HeldPackageList, InstalledPackageList, UpdateablePackageList

# Register your models here.
admin.site.register(Hosts)
admin.site.register(HostInfo)
admin.site.register(HeldPackageList)
admin.site.register(InstalledPackageList)
admin.site.register(UpdateablePackageList)
