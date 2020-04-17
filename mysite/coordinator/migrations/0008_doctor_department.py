# Generated by Django 3.0.5 on 2020-04-17 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coordinator', '0007_department_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='department',
            field=models.ForeignKey(default=1, help_text='Подразделение, к которому привязан врач', on_delete=django.db.models.deletion.SET_DEFAULT, to='coordinator.Department', verbose_name='Подразделение'),
        ),
    ]