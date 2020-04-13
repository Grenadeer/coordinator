from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Doctor, Record


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
    doctors = Doctor.objects.all()
    unrelated = Record.unassigned_by_date(work_date)

    return render(
        request,
        'coordinator/record_summary.html',
        {
            'doctors': doctors,
            'unrelated': unrelated,
            'work_date_get': work_date_get,
            'work_date': work_date,
        }
    )
