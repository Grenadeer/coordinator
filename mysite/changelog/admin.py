from django.contrib import admin
from .models import ChangeLog


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        'action_date',
        'model',
        'user',
        'record',
        'action',
    )
    readonly_fields = (
        'user',
    )
    list_filter = (
        'model',
        'action',
    )
