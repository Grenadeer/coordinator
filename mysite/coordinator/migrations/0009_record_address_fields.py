# Generated by Django 3.0.5 on 2020-04-18 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinator', '0008_doctor_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='address_apartment',
            field=models.CharField(default='', help_text='Квартира', max_length=10, verbose_name='Квартира'),
        ),
        migrations.AddField(
            model_name='record',
            name='address_building',
            field=models.CharField(default='', help_text='Дом', max_length=10, verbose_name='Дом'),
        ),
        migrations.AddField(
            model_name='record',
            name='address_street',
            field=models.CharField(default='', help_text='Улица', max_length=200, verbose_name='Улица'),
        ),
        migrations.AlterField(
            model_name='record',
            name='address',
            field=models.CharField(default='', help_text='Адрес вызова', max_length=200, verbose_name='Адрес'),
        ),
    ]
