# Generated by Django 3.0.5 on 2020-04-19 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coordinator', '0009_record_address_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='patient_birthdate',
            field=models.DateField(default='01.01.1900', help_text='Дата рождения пациента', verbose_name='Дата рождения'),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('middle_name', models.CharField(blank=True, default='', help_text='Отчество', max_length=100, verbose_name='Отчество')),
                ('department', models.ForeignKey(help_text='Подразделение', null=True, on_delete=django.db.models.deletion.SET_NULL, to='coordinator.Department', verbose_name='Подразделение')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]