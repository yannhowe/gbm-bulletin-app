from django.db import models
from django.contrib.auth.admin import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from paintstore.fields import ColorPickerField
from datetime import datetime, timedelta
import calendar

from django.forms import ModelForm, TextInput, DateInput
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

# Stores announcements for newsvine


class Announcement(models.Model):
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

    def is_published(self):
        import datetime
        today = datetime.date.today()
        if self.publish_start_date <= today <= self.publish_end_date:
            return True
        return False

    def __str__(self):
        return '%s - %s: %s' % (self.publish_start_date, self.publish_end_date, self.title)

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

# Stores read announcements


class ReadAnnouncement(models.Model):
    user = models.ForeignKey(User, db_index=True)
    announcement = models.ForeignKey(Announcement, db_index=True)

    def __str__(self):
        return 'User "%s" read "%s"' % (self.user, self.announcement)

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
    track_rsvp = models.BooleanField(default=False)

    def _get_date_display(self):
        if self.date_end == None:
            return self.date_start.strftime("%-d %b %Y")
        elif self.date_start.month == self.date_end.month:
            return '%s-%s' % (self.date_start.strftime("%-d"), self.date_end.strftime("%-d %b %Y"))

    date_display = property(_get_date_display)

    def __str__(self):
        return '%s - %s to %s' % (self.title, self.date_start, self.date_end)


class Signup(models.Model):
    # Service Names
    NOTGOING = 'notgoing'
    INTERESTED = 'interested'
    GOING = 'going'
    CHOICES = (
        (NOTGOING, 'Not Going'),
        (INTERESTED, 'Interested'),
        (GOING, 'Going')
    )

    user = models.ForeignKey(User, db_index=True)
    event = models.ForeignKey(Event, db_index=True)
    rsvp = models.CharField(
        max_length=30, choices=CHOICES, default=CHOICES[0][0])

    def __str__(self):
        return '%s - %s - %s' % (self.event, self.user, self.rsvp)


# Stores announcements for newsvine


class OrderOfService(models.Model):
    # Service Names
    SUN_MORN_ENG = 'sunday-morning-english'
    CHOICES = (
        (SUN_MORN_ENG, 'Sunday Morning - English Service'),)

    date = models.DateField(default=datetime.now)
    text = models.TextField(default='', blank=True)
    service_name = models.CharField(
        max_length=200, choices=CHOICES, default=CHOICES[0][0])

    def is_upcoming(self):
        import datetime
        today = datetime.date.today()
        if today <= self.date:
            return True
        return False

    def get_absolute_url(self):
        return reverse('orderofservice_edit', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' % (self.date, self.service_name)


# Add member details
class Detail(models.Model):

    member = models.OneToOneField(User, related_name='member_detail')

    gender = models.CharField(max_length=1, null=True, blank=True)

    date_record_created = models.DateField(default="2000-01-01")

    # important dates
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_marriage = models.DateField(null=True, blank=True)
    date_of_baptism = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    # phone numbers
#    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile_number = models.CharField(
        max_length=15, null=True, blank=True)  # validators should be a list
    # validators should be a list
    home_number = models.CharField(max_length=15, null=True, blank=True)

    # address
    address_block = models.CharField(max_length=12, null=True, blank=True)
    address_street = models.CharField(max_length=140, null=True, blank=True)
    address_unit = models.CharField(max_length=12, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=12, null=True, blank=True)

    # other details
    is_regular = models.BooleanField(default=True)
    is_member = models.BooleanField(default=False)

# family relationships


class Relationship(models.Model):
    MEMBER_RELATIONSHIP_CHOICES = (
        ('MO', 'Mother'),
        ('FA', 'Father'),
        ('BRO', 'Brother'),
        ('SIS', 'Sister'),
        ('SON', 'Son'),
        ('DAUG', 'Daughter'),
        ('GRMA', 'Grand Mother'),
        ('GRFA', 'Grand Father'),
        ('GRSON', 'Grand Son'),
        ('GRDAUG', 'Grand Daughter'),
    )

    member = models.OneToOneField(User, related_name='member_relationship')
    person = models.ForeignKey(User, related_name='person_relationship')
    relationship = models.CharField(
        max_length=10, choices=MEMBER_RELATIONSHIP_CHOICES)
