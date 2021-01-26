# Generated by Django 3.1.1 on 2020-10-08 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0006_employee_direction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='office',
            name='department',
        ),
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='departmentdirector',
            name='department',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='employee',
            name='direction',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='officeclerk',
            name='department',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='officeclerk',
            name='office',
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='Direction',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.DeleteModel(
            name='Office',
        ),
    ]
