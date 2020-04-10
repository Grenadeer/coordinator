from django.urls import path
from . import views

urlpatterns = [
    path('', views.record_summary, name='record_summary'),
    path('record/summary', views.record_summary, name='record_summary'),
]