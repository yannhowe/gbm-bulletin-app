# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-03 07:26
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import newswire.models
import paintstore.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=200)),
                ('body', models.TextField(default='', max_length=1200)),
                ('publish_start_date', models.DateField(default=datetime.datetime.now, verbose_name='Date to start publishing')),
                ('publish_end_date', models.DateField(default=newswire.models.get_default_publish_end_date, verbose_name='Date to end publishing')),
                ('link', models.CharField(blank=True, default='', max_length=400)),
                ('hidden', models.BooleanField(default=False)),
                ('under_review', models.BooleanField(default=True)),
                ('contact', models.CharField(blank=True, default='', max_length=200)),
                ('approver', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcement_approver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingFundCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default='0', max_digits=10)),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingFundYearGoal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=80, null=True)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default='0', max_digits=10)),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingFundYearPledge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=80, null=True)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default='0', max_digits=10)),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField(max_length=1200)),
                ('color', paintstore.fields.ColorPickerField(max_length=7)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, max_length=400, null=True)),
                ('date_start', models.DateField(default=datetime.datetime.now)),
                ('date_end', models.DateField(blank=True, null=True)),
                ('track_rsvp', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('type', models.CharField(choices=[('finance', 'Finance'), ('management', 'Management'), ('committee', 'Committee'), ('ministry', 'Ministry'), ('cg', 'Community Group'), ('tech', 'Technology')], max_length=32)),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderOfService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('text', models.TextField(blank=True, default='')),
                ('service_name', models.CharField(choices=[('sunday-morning-english', 'Sunday Morning - English Service')], default='sunday-morning-english', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=80, null=True)),
                ('last_name', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('prefered_name', models.CharField(blank=True, max_length=120, null=True)),
                ('maiden_name', models.CharField(blank=True, max_length=80, null=True)),
                ('gender', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female')], default='M', max_length=1, null=True)),
                ('date_record_updated', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_marriage', models.DateField(blank=True, null=True)),
                ('date_of_baptism', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=15, null=True)),
                ('home_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address_block', models.CharField(blank=True, max_length=12, null=True)),
                ('address_street', models.CharField(blank=True, max_length=140, null=True)),
                ('address_unit', models.CharField(blank=True, max_length=12, null=True)),
                ('country', models.CharField(blank=True, max_length=30, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=12, null=True)),
                ('is_regular', models.BooleanField(default=True)),
                ('is_member', models.BooleanField(default=False)),
                ('group', models.ManyToManyField(blank=True, related_name='group_profile', to='newswire.Group')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReadAnnouncement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.Announcement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(choices=[('MO', 'Mother'), ('FA', 'Father'), ('BRO', 'Brother'), ('SIS', 'Sister'), ('SON', 'Son'), ('DAUG', 'Daughter'), ('GRMA', 'Grand Mother'), ('GRFA', 'Grand Father'), ('GRSON', 'Grand Son'), ('GRDAUG', 'Grand Daughter')], max_length=10)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person_relationship', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_relationship', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=40)),
                ('value', models.CharField(db_index=True, max_length=160)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rsvp', models.CharField(choices=[('notgoing', 'Not Going'), ('interested', 'Interested'), ('going', 'Going')], default='notgoing', max_length=30)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SundayAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('english_congregation', models.PositiveSmallIntegerField(default=0)),
                ('chinese_congregation', models.PositiveSmallIntegerField(default=0)),
                ('childrens_church', models.PositiveSmallIntegerField(default=0)),
                ('preschoolers', models.PositiveSmallIntegerField(default=0)),
                ('nursery', models.PositiveSmallIntegerField(default=0)),
                ('under_review', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
                ('approver', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sunday_attendance_approver', to=settings.AUTH_USER_MODEL)),
                ('submitter', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sunday_attendance_submitter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Unsubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WeeklyVerse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=newswire.models.get_default_publish_end_date)),
                ('verse', models.TextField(default='', max_length=1200)),
                ('reference', models.CharField(default='', max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='buildingfundcollection',
            name='building_fund_year_goal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.BuildingFundYearGoal'),
        ),
        migrations.AddField(
            model_name='buildingfundcollection',
            name='building_fund_year_pledge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newswire.BuildingFundYearPledge'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='newswire.Category'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='submitter',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcement_submitter', to=settings.AUTH_USER_MODEL),
        ),
    ]