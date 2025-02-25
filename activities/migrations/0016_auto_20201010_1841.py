# Generated by Django 3.1.1 on 2020-10-10 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0015_auto_20201009_1243'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='departmentdirector',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='officeclerk',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='department',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
