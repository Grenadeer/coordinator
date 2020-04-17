from django.contrib import admin
from .models import Department, Doctor, Record, ServiceType


admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Record)
admin.site.register(ServiceType)
