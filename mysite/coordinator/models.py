from django.conf import settings
from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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

    #def records(self):
    #    records = Record.objects.filter(doctor=self)
    #    return records
