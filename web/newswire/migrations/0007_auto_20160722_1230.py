# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-22 04:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0006_auto_20160722_1120'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Data',
            new_name='DataPoint',
        ),
    ]
