from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Doctor, Record


@login_required
def record_summary(request):
    doctors = Doctor.objects.all()
    unrelated = Record.unassigned()
    return render(request, 'coordinator/record_summary.html', {'doctors': doctors, 'unrelated': unrelated})
