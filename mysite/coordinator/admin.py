from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Profile, Department, Doctor, Record, ServiceType


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_editable = ("name",)
    ordering = ("name",)


class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "department", "name")
    list_display_links = list_display
    list_filter = ("department",)
    ordering = ("department", "name")


class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_editable = ("name",)
    ordering = ("name",)


class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "department", "start_date", "get_address", "patient", "doctor", "service_type")
    list_display_links = list_display
    ordering = ("start_date",)
    list_filter = ("department", "doctor", "service_type")
    search_fields = ("patient",)
    date_hierarchy = "start_date"
    fieldsets = (
        (None, {"fields": ('department',)}),
        ("Временные отметки", {"fields": ('start_date', 'send_date', 'finish_date',)}),
        ("Адрес", {"fields": ('address_street', 'address_building', 'address_apartment',)}),
        ("Пациент", {"fields": ('patient', 'patient_birthdate', 'temperature',)}),
        (None, {"fields": ('service_type',)}),
    )
    save_on_top = True


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Record, RecordAdmin)

admin.site.register(Profile)

# admin.site.unregister(User)
# admin.site.unregister(Group)