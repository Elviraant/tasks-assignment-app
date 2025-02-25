# Generated by Django 3.1.1 on 2020-10-11 10:51

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0018_auto_20201010_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_sender_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='release_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 11, 13, 51, 5, 525645), verbose_name='release_date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_receiver_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
