from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Doctor


@login_required
def record_summary(request):
    doctors = Doctor.objects.all()
    return render(request, 'coordinator/record_summary.html', {'doctors': doctors})
