from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Department, Doctor, Record, ServiceType


@login_required
def record_summary(request):

    # Формат рабочей даты
    date_format = "%Y-%m-%d"
    # Получаем рабочую дату из сессии, если не задана, ставим текущую
    work_date_session = request.session.get('work_date', timezone.now().strftime(date_format))
    # Получаем рабочую дату из данных формы, если не задана, берем с предыдущего шага
    work_date_get = request.GET.get('work_date', work_date_session)
    # Формируем объект даты
    work_date = make_aware(datetime.strptime(work_date_get, date_format))
    # Обновляем данные сессии
    request.session['work_date'] = work_date_get

    # Количество пустых столбцов расписания, которые всегда видны
    record_max = 3

    # Основная таблица вызовов по докторам
    doctors_records = []
    doctors = Doctor.objects.all().filter(department=request.user.profile.department)
    for doctor in doctors:
        records = []
        record_count = 0
        for record in doctor.records_by_date(work_date):
            records.append(record)
            record_count += 1
        record_max = max(record_max, record_count)
        doctors_records.append(
            {
                'doctor': doctor,
                'records': records,
                'count': record_count,
            }
        )

    # Формируем статистику
    statistics = []
    departments = Department.objects.all()
    for department in departments:
        records_by_date = Record.objects.all().filter(department=department).filter(start_date__date=work_date)
        records_total = records_by_date.exclude(doctor=None).count()
        records_finished = records_by_date.exclude(finish_date=None)
        records_temperature = records_finished.filter(service_type__id=1).count()
        records_personally = records_finished.filter(service_type__id=2).count()
        records_telephone = records_finished.filter(service_type__id=3).count()
        statistics.append(
            {
                'department': department,
                'records_temperature': records_temperature,
                'records_personally': records_personally,
                'records_telephone': records_telephone,
                'records_total': records_total,
            }
        )

    # Перечень не назначенных вызовов
    unrelated = Record.unassigned_by_date_department(work_date, request.user.profile.department)

    return render(
        request,
        'coordinator/record_summary.html',
        {
            'work_date_get': work_date_get,
            'unrelated': unrelated,
            'doctors_records': doctors_records,
            'records_head': [i for i in range(1, record_max + 1)],
            'statistics': statistics,
        }
    )

@login_required
def record_assign(request, pk, id):
    record = get_object_or_404(Record, pk=pk)
    doctor = get_object_or_404(Doctor, pk=id)
    record.send_date = None
    record.assign(doctor)
    return redirect('record_summary')

@login_required
def record_send(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.send()
    return redirect('record_summary')

@login_required
def record_finish(request, pk, service_type_pk):
    record = get_object_or_404(Record, pk=pk)
    service_type = get_object_or_404(ServiceType, pk=service_type_pk)
    record.finish(service_type)
    return redirect('record_summary')


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = Record
    fields = [
        'address_street',
        'address_building',
        'address_apartment',
        'patient',
        'patient_birthdate',
        'temperature',
        'doctor'
    ]

    def get_form(self, form_class=None):
        form = super(RecordCreateView, self).get_form(form_class)
        form.fields['doctor'].queryset = Doctor.objects.filter(department=self.request.user.profile.department)
        return form

    def form_valid(self, form):
        form.instance.department = self.request.user.profile.department
        return super().form_valid(form)


class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Record
    fields = [
        'address_street',
        'address_building',
        'address_apartment',
        'patient',
        'patient_birthdate',
        'temperature',
        'service_type',
        'doctor'
    ]

    def get_form(self, form_class=None):
        form = super(RecordUpdateView, self).get_form(form_class)
        form.fields['doctor'].queryset = Doctor.objects.filter(department=self.request.user.profile.department)
        return form
