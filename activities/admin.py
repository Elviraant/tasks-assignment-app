from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import *

class EmployeeAdmin(UserAdmin):
    pass


class DepartmentDirectorAdmin(EmployeeAdmin):
    pass


class OfficeClerkAdmin(EmployeeAdmin):
    pass

EmployeeAdmin.fieldsets += ('Position', {'fields': ('direction',)}),
DepartmentDirectorAdmin.fieldsets += ('Position', {'fields': ('department',)}),
OfficeClerkAdmin.fieldsets += ('Position', {'fields': ('department', 'office')}),

# Register your models here.
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(DepartmentDirector, DepartmentDirectorAdmin)
admin.site.register(OfficeClerk, OfficeClerkAdmin)
admin.site.register(Activity)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Direction)
admin.site.register(Department)
admin.site.register(Office)
admin.site.register(Notification)
