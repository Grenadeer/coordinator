from django.urls import path
from django.views.generic import ListView, DetailView, CreateView
from . import views
from .models import Doctor, Record

urlpatterns = [
    path('', views.record_summary, name='record_summary'),
    path('record/summary', views.record_summary, name='record_summary'),
    path('record/assign/<int:pk>/<int:id>', views.record_assign, name='record_assign'),
    path('record/send/<int:pk>', views.record_send, name='record_send'),
    path('record/finish/<int:pk>', views.record_finish, name='record_finish'),

    path('doctor/', ListView.as_view(queryset=Doctor.objects.all(), template_name='coordinator/generic_list.html'),
         name='doctor_list'),
    path('doctor/<int:pk>', DetailView.as_view(model=Doctor, template_name='coordinator/generic_detail.html'), name='doctor_detail'),

    path('record/', ListView.as_view(queryset=Record.objects.all(), template_name='coordinator/generic_list.html'),
         name='record_list'),
    path('record/<int:pk>', DetailView.as_view(model=Record, template_name='coordinator/generic_detail.html'), name='record_detail'),
    path('record/create', CreateView.as_view(model=Record, fields=['address']), name='record_create'),
]