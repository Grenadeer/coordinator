from django.urls import path
from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView
from . import views
from .models import Doctor, Record
from .views import RecordCreateView, RecordUpdateView

urlpatterns = [

    # Doctors

    # views and forms
    path('doctor/', ListView.as_view(
        queryset=Doctor.objects.all(),
        ordering=[
            'department',
            'id',
        ],
        template_name='coordinator/doctor_list.html'
    ), name='doctor_list'),
    path('doctor/<int:pk>', DetailView.as_view(
        model=Doctor,
        template_name='coordinator/generic_detail.html'
    ), name='doctor_detail'),
    path('doctor/create', CreateView.as_view(
        model=Doctor,
        fields=[
            'department',
            'name',
        ],
    ), name='doctor_create'),
    path('doctor/update/<int:pk>', UpdateView.as_view(
        model=Doctor,
        fields=[
            'department',
            'name',
        ],
    ), name='doctor_update'),

    # Records

    # views and forms
    path('record/summary', views.record_summary, name='record_summary'),
    path('record/', ListView.as_view(
        queryset=Record.objects.all(),
        template_name='coordinator/record_list.html'
    ), name='record_list'),
    path('record/<int:pk>', DetailView.as_view(
        model=Record,
        template_name='coordinator/generic_detail.html'
    ), name='record_detail'),
    path('record/create', RecordCreateView.as_view(), name='record_create'),
    path('record/update/<int:pk>', RecordUpdateView.as_view(), name='record_update'),
    # methods
    path('record/assign/<int:pk>/<int:id>', views.record_assign, name='record_assign'),
    path('record/send/<int:pk>', views.record_send, name='record_send'),
    path('record/cancel/<int:pk>', views.record_cancel, name='record_cancel'),
    path('record/finish/<int:pk>/<int:service_type_pk>', views.record_finish, name='record_finish'),

    # Show records summary by default
    path('', RedirectView.as_view(
        pattern_name='record_summary',
        permanent=False
    ), name='index'),

]