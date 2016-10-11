# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-11 14:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0003_auto_20161011_2229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readannouncement',
            name='announcement',
        ),
        migrations.RemoveField(
            model_name='readannouncement',
            name='user',
        ),
        migrations.RemoveField(
            model_name='setting',
            name='user',
        ),
        migrations.RemoveField(
            model_name='unsubscription',
            name='category',
        ),
        migrations.RemoveField(
            model_name='unsubscription',
            name='user',
        ),
        migrations.DeleteModel(
            name='ReadAnnouncement',
        ),
        migrations.DeleteModel(
            name='Setting',
        ),
        migrations.DeleteModel(
            name='Unsubscription',
        ),
    ]
