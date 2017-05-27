from django.contrib import admin
from first_app.models import HeldPackageList, InstalledPackageList, UpdateablePackageList

# Register your models here.
admin.site.register(HeldPackageList)
admin.site.register(InstalledPackageList)
admin.site.register(UpdateablePackageList)
