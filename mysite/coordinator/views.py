from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import HiddenInput
from django.views.generic.edit import View, CreateView, UpdateView
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Department, Doctor, Record, ServiceType


@login_required
def record_summary(request):

    # Получаем рабочее подразделение
    if request.user.is_staff:
        work_department_id_session = request.session.get('work_department', request.user.profile.department.id)
        work_department_id = request.GET.get('work_department', work_department_id_session)
        request.session['work_department'] = work_department_id
        work_department = Department.objects.get(pk=work_department_id)
    else:
        work_department = request.user.profile.department

    # Получаем рабочую дату
    date_format = "%Y-%m-%d"
    work_date_session = request.session.get('work_date', timezone.now().strftime(date_format))
    work_date_get = request.GET.get('work_date', work_date_session)
    work_date = make_aware(datetime.strptime(work_date_get, date_format))
    # Обновляем данные сессии
    request.session['work_date'] = work_date_get

    # Количество пустых столбцов расписания, которые всегда видны
    record_max = 3

    # Основная таблица вызовов по докторам
    doctors_records = []
    doctors = Doctor.objects.all().filter(department=work_department)
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
        records_canceled = records_by_date.filter(service_type__id=1).count()
        records_temperature = records_finished.filter(service_type__id=2).count()
        records_personally = records_finished.filter(service_type__id=3).count()
        records_telephone = records_finished.filter(service_type__id=4).count()
        records_unfinished = records_by_date.filter(finish_date=None).count()
        statistics.append(
            {
                'department': department,
                'records_canceled': records_canceled,
                'records_temperature': records_temperature,
                'records_personally': records_personally,
                'records_telephone': records_telephone,
                'records_unfinished': records_unfinished,
                'records_total': records_total,
            }
        )
    records_by_date = Record.objects.all().filter(start_date__date=work_date)
    records_total = records_by_date.exclude(doctor=None).count()
    records_finished = records_by_date.exclude(finish_date=None)
    records_canceled = records_by_date.filter(service_type__id=1).count()
    records_temperature = records_finished.filter(service_type__id=2).count()
    records_personally = records_finished.filter(service_type__id=3).count()
    records_telephone = records_finished.filter(service_type__id=4).count()
    records_unfinished = records_by_date.filter(finish_date=None).count()
    statistics.append(
        {
            'department': 'Итого',
            'records_canceled': records_canceled,
            'records_temperature': records_temperature,
            'records_personally': records_personally,
            'records_telephone': records_telephone,
            'records_unfinished': records_unfinished,
            'records_total': records_total,
        }
    )

    # Перечень не назначенных вызовов
    unrelated = Record.unassigned_by_date_department(work_date, work_department)

    return render(
        request,
        'coordinator/record_summary.html',
        {
            'work_date_get': work_date_get,
            'work_department': work_department,
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
def record_cancel(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.cancel()
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
        work_department_id = self.request.session.get('work_department', self.request.user.profile.department.id)
        work_department = Department.objects.get(pk=work_department_id)
        form = super(RecordCreateView, self).get_form(form_class)
        form.fields['doctor'].queryset = Doctor.objects.filter(department=work_department)
        form.fields['address_street'].widget.attrs['onchange'] = 'getData(this.value);'
        return form

    def form_valid(self, form):
        work_department_id = self.request.session.get('work_department', self.request.user.profile.department.id)
        work_department = Department.objects.get(pk=work_department_id)
        form.instance.department = work_department
        return super().form_valid(form)


class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Record
    fields = [
        'department',
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
        work_department_id = self.request.session.get('work_department', self.request.user.profile.department.id)
        work_department = Department.objects.get(pk=work_department_id)
        form = super(RecordUpdateView, self).get_form(form_class)
        form.fields['doctor'].queryset = Doctor.objects.filter(department=work_department)
        if not self.request.user.is_staff:
            #form.fields['department'].widget.attrs['readonly'] = 'readonly'
            form.fields['department'].widget = HiddenInput()
        return form


class RecordListJSONView(View):
    def get(self, request):
        data = request.GET.get('data')
        records = list(
            Record.objects.all().filter(start_date__date=timezone.now()).filter(address_street__contains=data).values(
                "id",
                "address_street",
                "address_building",
                "address_apartment",
                "patient",
                "doctor__name",
            )
        )
        data = dict()
        print(records)
        data['records'] = records
        return JsonResponse(data)