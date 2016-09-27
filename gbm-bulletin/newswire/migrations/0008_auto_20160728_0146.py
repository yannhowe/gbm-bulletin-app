# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-27 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0007_auto_20160722_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapoint',
            name='notes',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='type',
            field=models.CharField(choices=[(b'finance', b'Finance'), (b'management', b'Management'), (b'committee', b'Committee'), (b'ministry', b'Ministry'), (b'cg', b'Community Group'), (b'tech', b'Technology')], max_length=32),
        ),
        migrations.RemoveField(
            model_name='profile',
            name='group',
        ),
        migrations.AddField(
            model_name='profile',
            name='group',
            field=models.ManyToManyField(blank=True, related_name='group_profile', to='newswire.Group'),
        ),
    ]
