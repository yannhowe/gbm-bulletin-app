from django.db import models
from django.contrib.auth.admin import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from paintstore.fields import ColorPickerField
from datetime import datetime, timedelta
import calendar

from django.forms import ModelForm, TextInput, DateInput
from suit.widgets import EnclosedInput, SuitDateWidget, SuitSplitDateTimeWidget

from django.db.models.signals import post_save
from django.dispatch import receiver


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
    submitter = models.ForeignKey(
        User, db_index=True, related_name="announcement_submitter", null=True, blank=True, default=None)
    approver = models.ForeignKey(
        User, db_index=True, related_name="announcement_approver", null=True, blank=True, default=None)
    title = models.CharField(max_length=200, default='')
    body = models.TextField(max_length=1200, default='')
    publish_start_date = models.DateField(
        'Date to start publishing', default=datetime.now)
    publish_end_date = models.DateField(
        'Date to end publishing', default=get_default_publish_end_date)
    category = models.ForeignKey(Category, default='')
    link = models.CharField(max_length=400, blank=True, default='')
    hidden = models.BooleanField(default=False)
    under_review = models.BooleanField(default=True)
    contact = models.CharField(max_length=200, blank=True, default='')

    def is_published(self):
        import datetime
        today = datetime.date.today()
        if self.publish_start_date <= today <= self.publish_end_date:
            return True
        return False

    def __str__(self):
        return '%s - %s: %s' % (self.publish_start_date, self.publish_end_date, self.title)

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
    description = models.TextField(max_length=400, null=True, blank=True)
    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField(blank=True, null=True)
    track_rsvp = models.BooleanField(default=False)

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

    def is_print(self):
        import datetime
        # coming sunday's date
        coming_sunday = datetime.date.today()
        while coming_sunday.weekday() != 6:
            coming_sunday += datetime.timedelta(1)

        if coming_sunday == self.date:
            return True
        return False

    def num_of_lines(self):
        i = 0
        for line in self.text:
            if "\n" in line:
                i += 1
        return i

    def get_absolute_url(self):
        return reverse('orderofservice_edit', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' % (self.date, self.service_name)


class Group(models.Model):
    GROUP_TYPE_CHOICES = (
        ('finance', 'Finance'),
        ('management', 'Management'),
        ('committee', 'Committee'),
        ('ministry', 'Ministry'),
        ('cg', 'Community Group'),
        ('tech', 'Technology'),
    )
    name = models.CharField(max_length=80)
    type = models.CharField(
        max_length=32, choices=GROUP_TYPE_CHOICES)
    notes = models.TextField(max_length=300, null=True, blank=True)


# Add member details
class Profile(models.Model):
    M = 'm'
    F = 'f'
    GENDER_CHOICES = (
        (M, 'Male'),
        (F, 'Female'),
    )

    user = models.OneToOneField(
        User, null=True, blank=True)
    group = models.ManyToManyField(
        Group, blank=True, related_name="group_profile")
    first_name = models.CharField(max_length=80, null=True, blank=True)
    last_name = models.CharField(max_length=80, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    prefered_name = models.CharField(max_length=120, null=True, blank=True)
    maiden_name = models.CharField(max_length=80, null=True, blank=True)

    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True, default='M')

    date_record_updated = models.DateField(
        null=True, blank=True, default=datetime.now)

    # important dates
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_marriage = models.DateField(null=True, blank=True)
    date_of_baptism = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    mobile_number = models.CharField(max_length=15, null=True, blank=True)
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

    def __str__(self):
        return '%s, %s %s' % (self.user, self.first_name, self.last_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

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

    user = models.OneToOneField(User, null=True, related_name='user_relationship')
    person = models.ForeignKey(User, null=True, related_name='person_relationship')
    relationship = models.CharField(
        max_length=10, choices=MEMBER_RELATIONSHIP_CHOICES)

    def __str__(self):
        return '%s, %s, %s' % (self.person, self.user, self.relationship)


class SundayAttendance(models.Model):
    submitter = models.ForeignKey(
        User, db_index=True, related_name="sunday_attendance_submitter", null=True, blank=True, default=None)
    approver = models.ForeignKey(
        User, db_index=True, related_name="sunday_attendance_approver", null=True, blank=True, default=None)
    date = models.DateField(default=datetime.now)
    english_congregation = models.PositiveSmallIntegerField(default=0)
    chinese_congregation = models.PositiveSmallIntegerField(default=0)
    childrens_church = models.PositiveSmallIntegerField(default=0)
    preschoolers = models.PositiveSmallIntegerField(default=0)
    nursery = models.PositiveSmallIntegerField(default=0)
    under_review = models.BooleanField(default=True)
    notes = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        return '%s' % (self.date)


class BuildingFundYearGoal(models.Model):
    name = models.TextField(max_length=80, null=True, blank=True)
    date = models.DateField(default=datetime.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    description = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date, formatted_amount)


class BuildingFundYearPledge(models.Model):
    name = models.TextField(max_length=80, null=True, blank=True)
    date = models.DateField(default=datetime.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    description = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date, formatted_amount)


class BuildingFundCollection(models.Model):
    date = models.DateField(default=datetime.now)
    building_fund_year_pledge = models.ForeignKey(BuildingFundYearPledge)
    building_fund_year_goal = models.ForeignKey(BuildingFundYearGoal)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notes = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date.strftime("%d/%m/%y"), formatted_amount)


class WeeklyVerse(models.Model):
    date = models.DateField(default=get_default_publish_end_date)
    verse = models.TextField(max_length=1200, default='')
    reference = models.CharField(max_length=40, default='')

    def __str__(self):
        return '%s - %s' % (self.date, self.reference)
