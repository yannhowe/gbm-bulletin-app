# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-16 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0005_auto_20161116_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='display_override',
            field=models.CharField(choices=[('hide', 'Hide Event'), ('show', 'Show Event'), ('default', 'Default: Displays 60 days in advance')], default='hide', max_length=30),
        ),
    ]
