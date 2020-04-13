from django.urls import path
from django.views.generic import ListView
from . import views
from .models import Doctor, Record

urlpatterns = [
    path('', views.record_summary, name='record_summary'),
    path('record/summary', views.record_summary, name='record_summary'),
    #path('record/assign/(int:pk)', views.record_assign, name='record_summary'),

    path('doctor/', ListView.as_view(queryset=Doctor.objects.all(), template_name='coordinator/generic_list.html'),
         name='doctor_list'),

    path('record/', ListView.as_view(queryset=Record.objects.all(), template_name='coordinator/generic_list.html'),
         name='record_list'),
]