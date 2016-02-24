from django.db import models
from django.contrib.auth.admin import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from paintstore.fields import ColorPickerField
from datetime import datetime, timedelta
import calendar

from django.forms import ModelForm,TextInput,DateInput
from suit.widgets import EnclosedInput, SuitDateWidget, SuitSplitDateTimeWidget

class Category(models.Model):

    class Meta:
        verbose_name_plural = "categories"
    name = models.CharField(max_length=80)
    description = models.TextField(max_length=1200)
    color = ColorPickerField()

    def __str__(self):
        return self.name

# Default publish for 7 days from today


def get_default_publish_end_date():
    return datetime.now() + timedelta(days=7)

# Stores posts for newsvine


class Post(models.Model):

    title = models.CharField(max_length=200, default='')
    body = models.TextField(max_length=1200, default='')
    publish_start_date = models.DateField(
        'Date to start publishing', default=datetime.now)
    publish_end_date = models.DateField(
        'Date to end publishing', default=get_default_publish_end_date)
    category = models.ForeignKey(Category, default='')
    link = models.CharField(max_length=400, blank=True, default='')
    hidden = models.BooleanField(default=False)
    contact = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return '%s %s' % (self.publish_start_date, self.title)

# Stores Weekly Summayry


class WeeklySummary(models.Model):

    class Meta:
        verbose_name_plural = "weekly summaries"
    date = models.DateField(default=datetime.now)
    attendance = models.SmallIntegerField(
        blank=True, default='')
    tithe_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    building_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    building_pledge_form_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    monthly_loan_servicing_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    c1_title = models.CharField(max_length=200, null=True, blank=True)
    c1_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    c2_title = models.CharField(max_length=200, null=True, blank=True)
    c2_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')
    c3_title = models.CharField(max_length=200, null=True, blank=True)
    c3_amt = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, default='')

    def __str__(self):
        return str(self.date)

# Stores all user settings


class Setting(models.Model):
    user = models.ForeignKey(User, db_index=True)
    key = models.CharField(max_length=40, db_index=True)
    value = models.CharField(max_length=160, db_index=True)

    def __str__(self):
        return '%s %s %s' % (self.user, self.key, self.value)

# Stores read posts


class ReadPost(models.Model):
    user = models.ForeignKey(User, db_index=True)
    post = models.ForeignKey(Post, db_index=True)

    def __str__(self):
        return 'User "%s" read "%s"' % (self.user, self.post)

# Stores user unsubscribed categories


class Unsubscription(models.Model):
    user = models.ForeignKey(User, db_index=True)
    category = models.ForeignKey(Category, db_index=True)

    def __str__(self):
        return '%s %s' % (self.user, self.category)

# Stores event list


class Event(models.Model):
    title = models.CharField(max_length=200)
    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField(blank=True, null=True)

    def _get_date_display(self):
        if self.date_end == None:
            return self.date_start.strftime("%-d %b %Y")
        elif self.date_start.month == self.date_end.month:
            return '%s-%s' % (self.date_start.strftime("%-d"), self.date_end.strftime("%-d %b %Y"))

    date_display = property(_get_date_display)

    def __str__(self):
        return '%s - %s to %s' % (self.title, self.date_start, self.date_end)


# Stores posts for newsvine


class OrderOfService(models.Model):
    # Service Names
    SUN_MORN_ENG = 'sunday-morning-english'
    SUN_MORN_CHI = 'sunday-morning-chinese'
    CHOICES = (
        (SUN_MORN_ENG, 'Sunday Morning - English Service'),
        (SUN_MORN_CHI, 'Sunday Morning - Chinese Service'))

    date = models.DateField(default=datetime.now)
    text = models.TextField(default='', blank=True)
    service_name = models.CharField(
        max_length=200, choices=CHOICES, default=CHOICES[0][0])

    def __str__(self):
        return '%s %s' % (self.date, self.service_name)
