# Generated by Django 3.0.5 on 2020-04-17 16:37


from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Department = apps.get_model("coordinator", "Department")
    db_alias = schema_editor.connection.alias
    Department.objects.using(db_alias).bulk_create([
        Department(id=1, name="Основное подразделение"),
    ])


def reverse_func(apps, schema_editor):
    # forwards_func() creates some instances,
    # so reverse_func() should delete them.
    Department = apps.get_model("coordinator", "Department")
    db_alias = schema_editor.connection.alias
    Department.objects.using(db_alias).filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('coordinator', '0006_service_type_initial_data'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
