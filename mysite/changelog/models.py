from django.db import models
from django.conf import settings


ACTION_CREATE = 'create';
ACTION_UPDATE = 'update';
ACTION_DELETE = 'delete';


class ChangeLog(models.Model):
    TYPE_ACTION_ON_MODEL = (
        (ACTION_CREATE, ('Создание')),
        (ACTION_UPDATE, ('Изменение')),
        (ACTION_DELETE, ('Удаление')),
    )

    action_date = models.DateTimeField(
        auto_now=True,
        help_text='',
        verbose_name='Дата/время',
    )
    model = models.CharField(
        max_length=255,
        null=True,
        help_text='Имя сущности',
        verbose_name='Данные',
    )
    record = models.IntegerField(
        null=True,
        help_text='Идентификатор записи',
        verbose_name='Запись',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Пользователь, выполнивший действие',
        verbose_name='Пользователь',
    )
    action = models.CharField(
        max_length=50,
        choices=TYPE_ACTION_ON_MODEL,
        null=True,
        help_text='Действие',
        verbose_name='Действие',
    )
    action_data = models.TextField(
        help_text='Изменяемые данные',
        verbose_name='Изменяемые данные',
    )

    class Meta():
        ordering = (
            'action_date',
        )
        verbose_name = 'Запись журнала изменений'
        verbose_name_plural = 'Записи журнала изменений'

    def __str__(self):
        return f'{self.id}'

    @classmethod
    def add(cls, instance, user, action, data, id=None):
        """Добавление записи в журнал изменений"""
        log = ChangeLog.objects.get(id=id) if id else ChangeLog()
        log.model = instance.__class__.__name__
        log.record = instance.pk
        if user:
            log.user = user
        log.action = action
        log.data = data.dump()
        log.save()
        return log.pk
