from django.contrib import admin
from .models import Doctor, Record, ServiceType


admin.site.register(Doctor)
admin.site.register(Record)
admin.site.register(ServiceType)