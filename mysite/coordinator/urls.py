from django.urls import path
from django.views.generic import ListView
from . import views
from .models import Doctor

urlpatterns = [
    path('', views.record_summary, name='record_summary'),
    path('record/summary', views.record_summary, name='record_summary'),

    path('doctor/', ListView.as_view(queryset=Doctor.objects.all(), template_name='coordinator/doctor_list.html'), name='doctor_list'),
]