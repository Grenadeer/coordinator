from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Doctor, Record, ServiceType


@login_required
def record_summary(request):
    date_format = "%Y-%m-%d"
    # Получаем рабочую дату из сессии, если не задана, ставим текущую
    work_date_session = request.session.get('work_date', timezone.now().strftime(date_format))
    # Получаем рабочую дату из данных формы, если не задана, берем с предыдущего шага
    work_date_get = request.GET.get('work_date', work_date_session)
    # Формируем объект даты
    work_date = make_aware(datetime.strptime(work_date_get, date_format))

    # Обновляем данные сессии
    request.session['work_date'] = work_date_get

    # Получаем наборы объектов
    record_max = 3
    doctors_records = []
    doctors = Doctor.objects.all()
    records_temperature = 0
    records_personally = 0
    records_telephone = 0
    for doctor in doctors:
        records = []
        record_count = 0
        for record in doctor.records_by_date(work_date):
            records.append(record)
            record_count += 1
            if record.is_finish():
                if record.is_personally():
                    records_personally += 1
                elif record.is_telephone():
                    records_telephone += 1
                else:
                    records_temperature += 1
        record_max = max(record_max, record_count)
        doctors_records.append(
            {
                'doctor': doctor,
                'records': records,
            }
        )
    unrelated = Record.unassigned_by_date(work_date)

    return render(
        request,
        'coordinator/record_summary.html',
        {
            'unrelated': unrelated,
            'doctors_records': doctors_records,
            'records_head': [i for i in range(1, record_max + 1)],
            'work_date_get': work_date_get,
            'records_temperature': records_temperature,
            'records_personally': records_personally,
            'records_telephone': records_telephone,
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
