# -*- coding: utf-8 -*-
from .forms import ProfileForm, ProfileFormFrontEnd, OrderOfServiceForm, AnnouncementForm, CategoryForm, WeeklySummaryForm, EventForm, DataPointForm, DataSeriesForm, AttendanceForm, WeeklyVerseForm
from .models import Announcement, Category, WeeklySummary, OrderOfService, Announcement, Event, ReadAnnouncement, Setting, Unsubscription, Signup, Profile, Relationship, DataPoint, DataSeries, WeeklyVerse
#from datetime import datetime, timedelta
import datetime
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template, get_template
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy
from email.Utils import formataddr
import os
import json
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


def get_upcoming_birthdays(person_list, days):
    person_list = person_list.distinct()  # ensure persons are only in the list once
    today = datetime.datetime.today()
    doblist = []
    doblist.extend(list(person_list.filter(
        date_of_birth__month=today.month, date_of_birth__day=today.day)))
    next_day = today + datetime.timedelta(days=1)
    for day in range(0, days):
        doblist.extend(list(person_list.filter(
            date_of_birth__month=next_day.month, date_of_birth__day=next_day.day, date_of_death__isnull=True)))
        next_day = next_day + datetime.timedelta(days=1)
    for dob in doblist:
        dob.date_of_birth = dob.date_of_birth.replace(
            year=datetime.datetime.today().year)
    return doblist


class BulletinListView(ListView):
    model = Announcement
    template_name = 'newswire/home.html'

    def get_context_data(self, **kwargs):
        context = super(BulletinListView, self).get_context_data(**kwargs)
        messages.info(self.request, '')
        now = datetime.datetime.now()
        today = datetime.datetime.today()

        # coming sunday's date
        coming_sunday = datetime.date.today()
        while coming_sunday.weekday() != 6:
            coming_sunday += datetime.timedelta(1)

        upcoming_service = None
        try:
            upcoming_service = OrderOfService.objects.order_by('date').filter(
                date__gte=datetime.datetime.now())[:1].get()
        except OrderOfService.DoesNotExist:
            upcoming_service = None
        context['orderofservice'] = upcoming_service

        upcoming_service_print = None
        try:
            upcoming_service_print = OrderOfService.objects.order_by('date').filter(
                date=coming_sunday).get()
        except OrderOfService.DoesNotExist:
            upcoming_service_print = None
        context['orderofservice_print'] = upcoming_service_print

        active_announcements = Announcement.objects.filter(
            publish_start_date__lte=now).filter(publish_end_date__gte=now)
        unread_active_announcements = Announcement.objects.exclude(
            readannouncement__announcement__id__in=active_announcements)
        published_announcements = unread_active_announcements.filter(publish_start_date__lte=today, publish_end_date__gte=today, hidden=False).extra(
            order_by=['-publish_start_date', 'publish_end_date'])
        context['announcements'] = published_announcements
        context['announcements_print'] = published_announcements[:7]
        context['more_annoucements_online_count'] = published_announcements.count() - 7

        all_birthdays = Profile.objects.exclude(date_of_birth=None)
        context['birthdays'] = get_upcoming_birthdays(all_birthdays, 7)

        try:
            latest_weeklysummary = WeeklySummary.objects.latest('date')
        except WeeklySummary.DoesNotExist:
            latest_weeklysummary = None
        context['weeklysummary'] = latest_weeklysummary

        try:
            latest_weeklyverse = WeeklyVerse.objects.latest('date')
        except WeeklyVerse.DoesNotExist:
            latest_weeklyverse = None
        context['weeklyverse'] = latest_weeklyverse

        try:
            active_events = Event.objects.filter(
                Q(date_end__gte=now) | Q(date_start__gte=now))
        except Event.DoesNotExist:
            active_events = None
        context['events'] = active_events.extra(
            order_by=['date_start'])

        if self.request.user.is_authenticated():
            try:
                signup_list = Signup.objects.filter(
                    event__in=active_events).filter(user=self.request.user)
            except Signup.DoesNotExist:
                signup_list = None
            context['signups'] = signup_list.all()

        if self.request.user.is_authenticated():
            try:
                signup_id_list = Signup.objects.filter(
                    event__in=active_events).filter(user=self.request.user).values_list('event_id', flat=True)
            except Signup.DoesNotExist:
                signup_id_list = None
            context['signup_id_list'] = signup_id_list.all()

        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class BulletinHomePageView(BulletinListView):
    template_name = 'newswire/home.html'


class BulletinPrintView(BulletinListView):
    template_name = 'newswire/cp/bulletin_print.html'


class OrderOfServiceList(ListView):
    model = OrderOfService
    # queryset = OrderOfService.objects.order_by('-date')
    template_name = 'newswire/cp/orderofservice_list.html'

    def get_context_data(self, **kwargs):
        context = super(OrderOfServiceList, self).get_context_data(**kwargs)
        now = datetime.datetime.now()

        liveorderofservice = None
        try:
            liveorderofservice = OrderOfService.objects.order_by('date').filter(
                date__gte=datetime.datetime.now())[:1].get()
        except OrderOfService.DoesNotExist:
            liveorderofservice = None
        context['live_orderofservice'] = liveorderofservice
        context['orderofservice'] = OrderOfService.objects.order_by('-date')

        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class OrderOfServiceCreate(CreateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceUpdate(UpdateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceDelete(DeleteView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    template_name = 'newswire/cp/orderofservice_confirm_delete.html'


class AnnouncementList(ListView):
    queryset = Announcement.objects.order_by(
        '-publish_start_date', 'publish_end_date')
    template_name = 'newswire/cp/announcement_list.html'


class AnnouncementCreate(CreateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class AnnouncementUpdate(UpdateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class AnnouncementDelete(DeleteView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    template_name = 'newswire/cp/announcement_confirm_delete.html'


class WeeklySummaryList(ListView):
    queryset = WeeklySummary.objects.order_by('-date')
    template_name = 'newswire/cp/weeklysummary_list.html'


class WeeklySummaryCreate(CreateView):
    model = WeeklySummary
    success_url = reverse_lazy('weeklysummary_list')
    form_class = WeeklySummaryForm
    template_name = 'newswire/cp/weeklysummary_form.html'


class WeeklySummaryUpdate(UpdateView):
    model = WeeklySummary
    success_url = reverse_lazy('weeklysummary_list')
    form_class = WeeklySummaryForm
    template_name = 'newswire/cp/weeklysummary_form.html'


class WeeklySummaryDelete(DeleteView):
    model = WeeklySummary
    success_url = reverse_lazy('weeklysummary_list')
    template_name = 'newswire/cp/weeklysummary_confirm_delete.html'


class EventList(ListView):
    queryset = Event.objects.order_by('-date_start')
    template_name = 'newswire/cp/event_list.html'


class EventCreate(CreateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventUpdate(UpdateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('event_list')
    template_name = 'newswire/cp/event_confirm_delete.html'


class CategoryList(ListView):
    queryset = Category.objects.all()
    template_name = 'newswire/cp/category_list.html'


class CategoryCreate(CreateView):
    model = Category
    success_url = reverse_lazy('category_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryUpdate(UpdateView):
    model = Category
    success_url = reverse_lazy('category_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryDelete(DeleteView):
    model = Category
    success_url = reverse_lazy('category_list')
    template_name = 'newswire/cp/category_confirm_delete.html'


class ProfileList(ListView):
    queryset = Profile.objects.all()
    template_name = 'newswire/cp/profile_list.html'


class ProfileCreate(CreateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileUpdate(UpdateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileDelete(DeleteView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    template_name = 'newswire/cp/profile_confirm_delete.html'


class ProfileDetailFrontEndView(DetailView):
    template_name = 'newswire/profile-detail.html'

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class ProfileUpdateFrontEndView(UpdateView):
    form_class = ProfileFormFrontEnd
    template_name = 'newswire/profile-update.html'

    def get_success_url(self):
        return reverse('profile_front_end_detail')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class DataPointList(ListView):
    queryset = DataPoint.objects.all()
    template_name = 'newswire/cp/datapoint_list.html'


class DataPointCreate(CreateView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    form_class = DataPointForm
    template_name = 'newswire/cp/datapoint_form.html'


class DataPointUpdate(UpdateView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    form_class = DataPointForm
    template_name = 'newswire/cp/datapoint_form.html'


class DataPointDelete(DeleteView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    template_name = 'newswire/cp/datapoint_confirm_delete.html'


class AttendanceList(ListView):
    # Filter for attendance objects
    queryset = DataPoint.objects.all()
    template_name = 'newswire/cp/attendance_list.html'


class AttendanceCreate(CreateView):
    model = DataPoint
    success_url = reverse_lazy('attendance_new')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceUpdate(UpdateView):
    model = DataPoint
    success_url = reverse_lazy('attendance_list')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceDelete(DeleteView):
    model = DataPoint
    success_url = reverse_lazy('attendance_list')
    template_name = 'newswire/cp/attendance_confirm_delete.html'


class DataSeriesList(ListView):
    queryset = DataSeries.objects.all()
    template_name = 'newswire/cp/dataseries_list.html'


class DataSeriesCreate(CreateView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    form_class = DataSeriesForm
    template_name = 'newswire/cp/dataseries_form.html'


class DataSeriesUpdate(UpdateView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    form_class = DataSeriesForm
    template_name = 'newswire/cp/dataseries_form.html'


class DataSeriesDelete(DeleteView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    template_name = 'newswire/cp/dataseries_confirm_delete.html'


class WeeklyVerseList(ListView):
    queryset = WeeklyVerse.objects.all()
    template_name = 'newswire/cp/weeklyverse_list.html'


class WeeklyVerseCreate(CreateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseUpdate(UpdateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseDelete(DeleteView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    template_name = 'newswire/cp/weeklyverse_confirm_delete.html'


class RsvpUpdateView(DetailView):

    model = Signup

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            the_user = request.user
            the_rsvp = request.POST.get('the_rsvp')
            the_event = Event.objects.get(pk=request.POST.get('the_event'))
            the_pk = ""
            response_data = {}
            signup = Signup()

            try:
                the_pk = Signup.objects.get(event=the_event, user=the_user).pk
                signup.pk = the_pk
            except:
                pass
            signup.user = the_user
            signup.event = the_event
            signup.rsvp = the_rsvp
            signup.save()

            response_data['the_rsvp'] = signup.rsvp
            response_data['the_event'] = signup.event.pk

            if the_pk:
                response_data['record'] = "updated"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                response_data['record'] = "created"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )

    def get_success_url(self):
        return reverse('home')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class RsvpListView(ListView):

    model = Signup
    template_name = 'newswire/cp/rsvp_list.html'

    def get_context_data(self, **kwargs):
        context = super(RsvpListView, self).get_context_data(**kwargs)
        event_signups = []
        try:
            context['signups'] = Signup.objects.order_by('event', 'rsvp')
        except Event.DoesNotExist:
            pass
        return context


class RsvpListViewRaw(ListView):

    model = Signup
    template_name = 'newswire/cp/rsvp_list_raw.html'

    def get_context_data(self, **kwargs):
        context = super(RsvpListViewRaw, self).get_context_data(**kwargs)
        event_signups = []
        try:
            context['signups'] = Signup.objects.order_by('event', 'rsvp')
        except Event.DoesNotExist:
            pass
        return context


class ControlPanelHomeView(ListView):

    model = Announcement
    template_name = 'newswire/cp/home.html'

    def get_context_data(self, **kwargs):
        context = super(ControlPanelHomeView, self).get_context_data(**kwargs)
        messages.info(self.request, '')
        now = datetime.datetime.now()

        upcoming_service = None
        try:
            upcoming_service = OrderOfService.objects.order_by('date').filter(
                date__gte=datetime.datetime.now())[:1].get()
        except OrderOfService.DoesNotExist:
            upcoming_service = None
        context['orderofservice'] = upcoming_service

        active_announcements = Announcement.objects.filter(
            publish_start_date__lte=now).filter(publish_end_date__gte=now)
        unread_active_announcements = Announcement.objects.exclude(
            readannouncement__announcement__id__in=active_announcements)
        context['announcements'] = unread_active_announcements.extra(
            order_by=['-publish_start_date'])

        try:
            latest_weeklysummary = WeeklySummary.objects.latest('date')
        except WeeklySummary.DoesNotExist:
            latest_weeklysummary = None
        context['weeklysummary'] = latest_weeklysummary

        try:
            active_events = Event.objects.filter(
                Q(date_end__gte=now) | Q(date_start__gte=now))
        except Event.DoesNotExist:
            active_events = None
        context['events'] = active_events.extra(
            order_by=['date_start'])

        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


def send_bulletin(request):

    message = template_email(
        template_name='emails/bulletin',
        subject='GBM Bulletin',
        to=['yannhowe@gmail.com']
    )
    message.send()
    messages.add_message(request, messages.INFO,
                         'Bulletin emailed to you.')
    return HttpResponseRedirect(reverse('home'))


def template_email(template_name, extra_context=None, *args, **kwargs):
    """
    Thanks to https://gist.github.com/SmileyChris/5881290

    Return an :cls:`~django.core.mail.EmailMessage` with the body (and
    optionally, the subject) set from django templates.
    :param template_name: The template name, or partial template name.
    :param extra_context: A dictionary of context data to pass to the email
        templates.
    Passing the full template name will render the email body using this
    template. If the template extension is ``htm`` or ``html``, the message
    mime subtype will be changed to ``html``. For example::
        message = template_email(
            template_name='emails/alert.txt', subject="Alert!",
            to=['bob@example.com'])
        message.send()
    Passing a partial template allows a plain text body, an HTML alternative,
    and the subject to all be templates. For example, calling
    ``template_email(template_name='emails/welcome')`` will look for the
    following templates:
    * ``emails/welcome_subject.txt`` will set the message's subject line. Only
      the first non-blank line of this file will be used.
    * ``emails/welcome.txt`` will be the plain text body.
    * ``emails/welcome.html`` will be the HTML alternative if a plain text body
      is also found, otherwise it'll be the body and the message mime subtype
      will be changed to ``html``.
    If neither the plain text or HTML template exist, a
    :cls:`~django.template.TemplateDoesNotExist` exception will be raised. The
    subject template is optional.
    The subject and plain text body templates are rendered with auto-escape
    turned off.
    """
    message = mail.EmailMultiAlternatives(*args, **kwargs)

    context = template.Context(extra_context)

    html_template_names = ['{}.html'.format(template_name)]
    txt_template_names = ['{}.txt'.format(template_name)]
    if os.path.splitext(template_name)[1].lower() in ('.htm', '.html'):
        html_template_names.append(template_name)
    else:
        txt_template_names.append(template_name)

    # Get the HTML body.
    try:
        html = select_template(html_template_names).render(context)
    except template.TemplateDoesNotExist:
        html = None

    print html

    # The remainder of the templates are text only, so turn off autoescaping.
    context.autoescape = False

    # Get the plain-text body.
    try:
        txt = select_template(txt_template_names).render(context)
    except template.TemplateDoesNotExist:
        if not html:
            # Neither body template exists.
            raise
        txt = None

    # Get the subject.
    try:
        subject = (
            get_template('{}_subject.txt'.format(template_name))
            .render(context)
        )
        message.subject = subject.strip().splitlines()[0]
    except template.TemplateDoesNotExist:
        pass

    if txt:
        message.body = txt
        if html:
            message.attach_alternative(html, 'text/html')
    else:
        message.content_subtype = 'html'
        message.body = html

    return message


def template_mail_managers(**kwargs):
    return _template_email_convenience(to=settings.MANAGERS, **kwargs)


def template_mail_admins(**kwargs):
    return _template_email_convenience(to=settings.ADMINS, **kwargs)


def _template_email_convenience(to, fail_silently=False, **kwargs):
    to = [formataddr(recipient) for recipient in to]
    final_kwargs = {'from_email': settings.SERVER_EMAIL}
    final_kwargs.update(kwargs)

    message = template_email(to=to, **final_kwargs)
    if settings.EMAIL_SUBJECT_PREFIX:
        message.subject = (
            settings.EMAIL_SUBJECT_PREFIX + message.subject)
    message.send(fail_silently=fail_silently)
