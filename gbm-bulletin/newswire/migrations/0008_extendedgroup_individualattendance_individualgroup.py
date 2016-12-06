# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-03 05:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('newswire', '0007_auto_20161116_1352'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedGroup',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.Group')),
                ('group_type', models.IntegerField(choices=[(0, 'Community Group'), (1, 'Management'), (2, 'Committee')])),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
                ('date_formed', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('date_dissolved', models.DateField(blank=True, null=True)),
                ('meeting_day', models.IntegerField(blank=True, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'), (7, 'Irregular')], null=True)),
                ('meeting_time', models.TimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='IndividualAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('attendance', models.IntegerField(choices=[(0, 'Present'), (1, 'Absent'), (2, 'Excused'), (3, 'Unknown')])),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.ExtendedGroup')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('date_left', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('active', models.BooleanField(default=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.ExtendedGroup')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.Profile')),
            ],
        ),
    ]
