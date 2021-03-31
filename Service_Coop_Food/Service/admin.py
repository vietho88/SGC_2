from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Role)
admin.site.register(Site)
admin.site.register(UserCoop)
admin.site.register(TypeProduct)
admin.site.register(Permission)
# admin.site.register(UserCoopBill)
# admin.site.register(Bill)
# admin.site.register(GroupBill)
admin.site.register(RolePermission)
admin.site.register(PermissionChangeStatus)
admin.site.register(StatusBill)
admin.site.register(TypeLog)
# admin.site.unregister(Group)
