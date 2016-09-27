# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-15 04:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0011_auto_20160913_0832'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildingFundCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default=b'0', max_digits=10)),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingFundYearGoal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=80, null=True)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default=b'0', max_digits=10)),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingFundYearPledge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=80, null=True)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, default=b'0', max_digits=10)),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
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
    ]
