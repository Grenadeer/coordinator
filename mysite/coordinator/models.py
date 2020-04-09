from django.conf import settings
from django.db import models
#from django.utils import timezone


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Укажите учетную запись пользователя",
        verbose_name="Учетная запись",
    )
    name = models.CharField(
        max_length=100,
        help_text="Фамилия И.О.",
        verbose_name="Имя врача",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def records(self):
        records = Record.objects.filter(doctor=self)
        return records


class Record(models.Model):
    date = models.DateField(
        auto_now_add=True,
        help_text="Дата регистрации вызова",
        verbose_name="Дата вызова",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='doctor_records',
        help_text="Врач назначенный на вызов",
        verbose_name="Врач",
    )
    address = models.CharField(
        max_length=200,
        help_text="Адрес вызова",
        verbose_name="Адрес",
    )
    record_order = models.IntegerField(
        help_text="Порядковый номер вызова",
        verbose_name="Порядок",
    )

    def __str__(self):
        temp = "Вызов от " + self.date.strftime('%d.%m.%Y') + " по адресу <" + self.address + ">"
        if self.doctor is None:
            temp = temp + " не назначен"
        else:
            temp = temp + " назначен " + str(self.doctor)
        return temp

    class Meta:
        verbose_name = "Вызов"
        verbose_name_plural = "Вызовы"

    @staticmethod
    def unrelated():
        return Record.objects.filter(doctor=None)