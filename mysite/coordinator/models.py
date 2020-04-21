from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Наименование подразделения",
        verbose_name="Наименование",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Подразделение",
        verbose_name="Подразделение",
    )
    middle_name = models.CharField(
        max_length=100,
        default="",
        blank=True,
        help_text="Отчество",
        verbose_name="Отчество",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.user.__str__()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


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
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_DEFAULT,
        default=1,
        #related_name='doctor_records',
        help_text="Подразделение, к которому привязан врач",
        verbose_name="Подразделение",
    )
    temperature = models.BooleanField(
        default=False,
        help_text="Обслуживает температурные вызовы",
        verbose_name="Температура",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def get_absolute_url(self):
        return "/doctor/"

    def get_list_fields(self):
        fields = []
        for field in self._meta.fields:
            fields.append({
                'name': field.name,
                'verbose_name': field.verbose_name,
                'value': field.value_from_object(self)
            })
        return fields

    def get_detail_fields(self):
        fields = []
        for field in self._meta.fields:
            fields.append({
                'name': field.name,
                'verbose_name': field.verbose_name,
                'value': field.value_from_object(self)
            })
        return fields

    def get_verbose_name(self):
        return self._meta.verbose_name

    def get_verbose_name_plural(self):
        return self._meta.verbose_name_plural

    def records(self):
        records = Record.objects.filter(doctor=self)
        return records

    def records_by_date(self, date):
        records = Record.objects.filter(doctor=self).filter(start_date__date=date)
        return records


class ServiceType(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Адрес вызова",
        verbose_name="Адрес",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид обслуживания"
        verbose_name_plural = "Виды обслуживания"


class Record(models.Model):
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Дата регистрации вызова",
        verbose_name="Поступил",
    )
    send_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Дата/время передачи вызова",
        verbose_name="Передан",
    )
    finish_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Дата/время завершения вызова",
        verbose_name="Завершен",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        #related_name=
        help_text="Подразделение",
        verbose_name="Подразделение",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_records',
        help_text="Врач назначенный на вызов",
        verbose_name="Врач",
    )
    address = models.CharField(
        max_length=200,
        default="",
        blank=True,
        help_text="Адрес вызова",
        verbose_name="Адрес",
    )
    address_street = models.CharField(
        max_length=200,
        default="",
        help_text="Улица",
        verbose_name="Улица",
    )
    address_building = models.CharField(
        max_length=10,
        default="",
        help_text="Дом",
        verbose_name="Дом",
    )
    address_apartment = models.CharField(
        max_length=10,
        default="",
        blank=True,
        help_text="Квартира",
        verbose_name="Квартира",
    )
    patient = models.CharField(
        max_length=150,
        default="",
        help_text="Фамилия И.О.",
        verbose_name="Пациент",
    )
    patient_birthdate = models.DateField(
        default='01.01.1900',
        help_text="Дата рождения пациента",
        verbose_name="Дата рождения",
    )
    temperature = models.BooleanField(
        default=False,
        help_text="Температурный вызов",
        verbose_name="Температура",
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Как был обслужен вызов",
        verbose_name="Вид обслуживания",
    )
    record_order = models.IntegerField(
        help_text="Порядковый номер вызова",
        verbose_name="Порядок",
        default=0,
    )

    def get_absolute_url(self):
        # TODO: Костыль - нужно проработать возврат на нужную страницу в зависимости от источника
        #return "/record/%i" % self.id
        return "/"

    def __str__(self):
        temp = "Вызов от " + self.start_date.strftime('%d.%m.%Y') + " по адресу <" +\
               self.address_street + " " +\
               self.address_building + "-" +\
               self.address_apartment +\
               ">"
        if self.doctor is None:
            temp = temp + " не назначен"
        else:
            temp = temp + " назначен " + str(self.doctor)
        return temp

    class Meta:
        verbose_name = "Вызов"
        verbose_name_plural = "Вызовы"

    def get_address(self):
        return self.address_street + " " + self.address_building + "-" + self.address_apartment

    def get_list_fields(self):
        fields = []
        for field in self._meta.fields:
            fields.append({
                'name': field.name,
                'verbose_name': field.verbose_name,
                'value': field.value_from_object(self)
            })
        return fields

    def get_detail_fields(self):
        fields = []
        for field in self._meta.fields:
            fields.append({
                'name': field.name,
                'verbose_name': field.verbose_name,
                'value': field.value_from_object(self)
            })
        return fields

    def get_verbose_name(self):
        return self._meta.verbose_name

    def get_verbose_name_plural(self):
        return self._meta.verbose_name_plural

    def is_sent(self):
        return not self.send_date is None

    def is_finish(self):
        return not self.finish_date is None

    def is_temperature(self):
        return self.temperature

    def is_personally(self):
        return self.service_type.pk == 2

    def is_telephone(self):
        return self.service_type.pk == 3

    @staticmethod
    def unassigned():
        return Record.objects.filter(doctor=None)

    @staticmethod
    def unassigned_by_date(date):
        return Record.objects.filter(doctor=None).filter(start_date__date=date)

    @staticmethod
    def unassigned_by_date_department(date, department):
        return Record.objects.filter(doctor=None).filter(department=department).filter(start_date__date=date)

    def assign(self, doctor):
        self.doctor = doctor
        self.save()
        return

    def send(self):
        self.send_date = timezone.now()
        self.save()
        return

    def finish(self, service_type):
        self.finish_date = timezone.now()
        self.service_type = service_type
        self.save()
        return
