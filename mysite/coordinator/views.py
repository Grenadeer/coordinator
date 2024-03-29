from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import HiddenInput
from django.views.generic.base import View, RedirectView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.dates import DayArchiveView, TodayArchiveView
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, date
from .models import Department, Doctor, Record, ServiceType


# Doctor views

class DoctorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'coordinator.view_doctor'
    model = Doctor
    ordering = [
                   'department',
                   'id',
               ]


class DoctorScheduleView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'coordinator.view_own_record'
    template_name = "coordinator/doctor_schedule.html"

    def get_queryset(self):
        work_date = timezone.localdate()
        return Record.objects.all().\
            filter(doctor=self.request.user.doctor).\
            filter(start_date__date=work_date).\
            exclude(send_date=None)


# class Doctor


class RecordSummary(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'coordinator.view_record'
    raise_exception = True
    template_name = "coordinator/record_summary.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # Получаем рабочее подразделение
        if self.request.user.is_staff:
            work_department_id_session = self.request.session.get(
                'work_department',
                self.request.user.profile.department.id
            )
            work_department_id = self.request.GET.get('work_department', work_department_id_session)
            self.request.session['work_department'] = work_department_id
            work_department = Department.objects.get(pk=work_department_id)
        else:
            work_department = self.request.user.profile.department
        context['work_department'] = work_department

        # Получаем рабочую дату
        date_format = "%Y-%m-%d"
        work_date_session = self.request.session.get('work_date', timezone.now().strftime(date_format))
        work_date_get = self.request.GET.get('work_date', work_date_session)
        work_date = make_aware(datetime.strptime(work_date_get, date_format))
        # Обновляем данные сессии
        self.request.session['work_date'] = work_date_get
        context['work_date_get'] = work_date_get

        # Основная таблица вызовов по докторам
        record_max = 3  # Количество пустых столбцов расписания, которые всегда видны
        doctors_records = []
        doctors = Doctor.objects.all().filter(department=work_department)
        for doctor in doctors:
            records = []
            record_count = 0
            record_done_count = 0
            for record in doctor.records_by_date(work_date):
                records.append(record)
                record_count += 1
                if record.is_finish():
                    record_done_count += 1
            record_max = max(record_max, record_count)
            doctors_records.append(
                {
                    'doctor': doctor,
                    'records': records,
                    'count': record_count,
                    'done_count': record_done_count,
                }
            )
        context['records_head'] = [i for i in range(1, record_max + 1)]
        context['doctors_records'] = doctors_records

        # Формируем статистику
        statistics = []
        # По подразделениям
        departments = Department.objects.all()
        for department in departments:
            records_by_date = Record.objects.all().filter(department=department).filter(start_date__date=work_date)
            records_total = records_by_date.count()
            records_finished = records_by_date.exclude(finish_date=None)
            records_canceled = records_by_date.filter(service_type__id=1).count()
            records_temperature = records_finished.filter(service_type__id=2).count()
            records_personally = records_finished.filter(service_type__id=3).count()
            records_telephone = records_finished.filter(service_type__id=4).count()
            records_didnt_open = records_finished.filter(service_type__id=5).count()
            records_unfinished = records_by_date.filter(finish_date=None).exclude(service_type__id=1).count()
            statistics.append(
                {
                    'department': department,
                    'records_canceled': records_canceled,
                    'records_temperature': records_temperature,
                    'records_personally': records_personally,
                    'records_telephone': records_telephone,
                    'records_didnt_open': records_didnt_open,
                    'records_unfinished': records_unfinished,
                    'records_total': records_total,
                }
            )
        # Итоговая
        records_by_date = Record.objects.all().filter(start_date__date=work_date)
        records_total = records_by_date.count()
        records_finished = records_by_date.exclude(finish_date=None)
        records_canceled = records_by_date.filter(service_type__id=1).count()
        records_temperature = records_finished.filter(service_type__id=2).count()
        records_personally = records_finished.filter(service_type__id=3).count()
        records_telephone = records_finished.filter(service_type__id=4).count()
        records_didnt_open = records_finished.filter(service_type__id=5).count()
        records_unfinished = records_by_date.filter(finish_date=None).exclude(service_type__id=1).count()
        statistics.append(
            {
                'department': 'Итого',
                'records_canceled': records_canceled,
                'records_temperature': records_temperature,
                'records_personally': records_personally,
                'records_telephone': records_telephone,
                'records_didnt_open': records_didnt_open,
                'records_unfinished': records_unfinished,
                'records_total': records_total,
            }
        )
        context['statistics'] = statistics

        # Перечень не назначенных вызовов
        context['unrelated'] = Record.unassigned_by_date_department(work_date, work_department)

        # Перечень подразделений для выбора
        context['departments'] = Department.objects.all

        return context


class RecordManagement(RecordSummary):
    template_name = 'coordinator/record_management.html'


@login_required()
@permission_required('coordinator.view_record', raise_exception=True)
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
    # По подразделениям
    departments = Department.objects.all()
    for department in departments:
        records_by_date = Record.objects.all().filter(department=department).filter(start_date__date=work_date)
        records_total = records_by_date.exclude(doctor=None).count()
        records_finished = records_by_date.exclude(finish_date=None)
        records_canceled = records_by_date.filter(service_type__id=1).count()
        records_temperature = records_finished.filter(service_type__id=2).count()
        records_personally = records_finished.filter(service_type__id=3).count()
        records_telephone = records_finished.filter(service_type__id=4).count()
        records_didnt_open = records_finished.filter(service_type__id=5).count()
        records_unfinished = records_by_date.filter(finish_date=None).count()
        statistics.append(
            {
                'department': department,
                'records_canceled': records_canceled,
                'records_temperature': records_temperature,
                'records_personally': records_personally,
                'records_telephone': records_telephone,
                'records_didnt_open': records_didnt_open,
                'records_unfinished': records_unfinished,
                'records_total': records_total,
            }
        )
    # Итоговая
    records_by_date = Record.objects.all().filter(start_date__date=work_date)
    records_total = records_by_date.exclude(doctor=None).count()
    records_finished = records_by_date.exclude(finish_date=None)
    records_canceled = records_by_date.filter(service_type__id=1).count()
    records_temperature = records_finished.filter(service_type__id=2).count()
    records_personally = records_finished.filter(service_type__id=3).count()
    records_telephone = records_finished.filter(service_type__id=4).count()
    records_didnt_open = records_finished.filter(service_type__id=5).count()
    records_unfinished = records_by_date.filter(finish_date=None).count()
    statistics.append(
        {
            'department': 'Итого',
            'records_canceled': records_canceled,
            'records_temperature': records_temperature,
            'records_personally': records_personally,
            'records_telephone': records_telephone,
            'records_didnt_open': records_didnt_open,
            'records_unfinished': records_unfinished,
            'records_total': records_total,
        }
    )

    # Перечень не назначенных вызовов
    unrelated = Record.unassigned_by_date_department(work_date, work_department)

    # Перечень подразделений для выбора
    departments = Department.objects.all

    return render(
        request,
        'coordinator/record_summary.html',
        {
            'work_date_get': work_date_get,
            'work_department': work_department,
            'departments': departments,
            'unrelated': unrelated,
            'doctors_records': doctors_records,
            'records_head': [i for i in range(1, record_max + 1)],
            'statistics': statistics,
        }
    )


@permission_required('coordinator.change_record', raise_exception=True)
def record_assign(request, pk, id):
    record = get_object_or_404(Record, pk=pk)
    doctor = get_object_or_404(Doctor, pk=id)
    record.assign(doctor)
    return redirect('record_summary')


@permission_required('coordinator.change_record', raise_exception=True)
def record_cancel(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.cancel()
    return redirect('record_summary')


@permission_required('coordinator.change_record', raise_exception=True)
def record_send(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.send()
    return redirect('record_summary')


@permission_required('coordinator.change_record', raise_exception=True)
def record_finish(request, pk, service_type_pk):
    next_url = request.GET.get('next', 'record_summary')
    record = get_object_or_404(Record, pk=pk)
    service_type = get_object_or_404(ServiceType, pk=service_type_pk)
    record.finish(service_type)
    return redirect(next_url)


class RecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'coordinator.add_record'
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


class RecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'coordinator.change_record'
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
            form.fields['department'].widget = HiddenInput()
        return form



class RecordListJSONView(PermissionRequiredMixin, View):
    permission_required = 'coordinator.view_record'

    def get(self, request):
        data = request.GET.get('data')
        records = list(
            Record.objects.all().filter(start_date__date=timezone.now()).filter(address_street__contains=data).values(
                "id",
                "department__name",
                "address_street",
                "address_building",
                "address_apartment",
                "patient",
                "doctor__name",
                "service_type__name",
            )
        )
        data = dict()
        data['records'] = records
        print(records)
        return JsonResponse(data)


class RecordDayArchiveView(LoginRequiredMixin, PermissionRequiredMixin, DayArchiveView):
    permission_required = 'coordinator.view_record'
    model = Record
    date_field = "start_date"
    allow_future = True
    day_format = '%d'
    month_format = '%m'
    year_format = '%Y'


class RecordTodayArchiveView(LoginRequiredMixin, PermissionRequiredMixin, TodayArchiveView):
    permission_required = 'coordinator.view_record'
    model = Record
    date_field = "start_date"
    day_format = '%d'
    month_format = '%m'
    year_format = '%Y'

    def get_dated_items(self):
        prev_day = self.get_previous_day(self._get_next_day(date.today()))
        if prev_day is None:
            raise Http404('В базе данных еще нет записей')
        else:
            return self._get_dated_items(prev_day)


class RootRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Координаторы
        if self.request.user.groups.filter(pk=1).exists():
            redirect_url = '/record/summary/'
        elif self.request.user.groups.filter(pk=2).exists():
            redirect_url = '/doctor/schedule/'
        elif self.request.user.groups.filter(pk=3).exists():
            redirect_url = '/record/management/'
        else:
            redirect_url = '/help/no_group/'
        return redirect_url
