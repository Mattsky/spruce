# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-31 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0004_auto_20170531_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heldpackagelist',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='installedpackagelist',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
