# -*- coding: utf-8 -*-
from .forms import ProfileForm, ProfileFormFrontEnd, OrderOfServiceForm, AnnouncementForm, CategoryForm, EventForm, DataPointForm, DataSeriesForm, AttendanceForm, WeeklyVerseForm
from .models import Announcement, Category, OrderOfService, Announcement, Event, ReadAnnouncement, Setting, Unsubscription, Signup, Profile, Relationship, DataPoint, DataSeries, WeeklyVerse
# from datetime import datetime, timedelta
import datetime
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import mail, serializers
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum, F, When, Case
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template, get_template, render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy
from email.Utils import formataddr
import os
import json
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from constance import config
from weasyprint import HTML, CSS

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect


class LoginRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600
    """
    View mixin which requires that the user is authenticated.
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(self, request, *args, **kwargs)


class StaffRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperUserRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600
    """
    View mixin which requires that the authenticated user is a super user
    (i.e. `is_superuser` is True).
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(SuperUserRequiredMixin, self).dispatch(request,
                                                            *args, **kwargs)


class PdfResponseMixin(object, ):

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data()
        template = self.get_template_names()[0]
        html_string = render_to_string(template, context)
        rendered_html = HTML(string=html_string)
        pdf_file = rendered_html.write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="mypdf.pdf"'
        return response


class BulletinListView(ListView):
    model = Announcement
    template_name = 'newswire/home.html'

    def get_coming_sunday(self, date):
        # coming sunday's date
        coming_sunday = date
        while coming_sunday.weekday() != 6:
            coming_sunday += datetime.timedelta(1)
        return coming_sunday

    def get_upcoming_birthdays(self, person_list, days, from_date=datetime.datetime.today()):
        person_list = person_list.distinct()  # ensure persons are only in the list once
        doblist = []
        doblist.extend(list(person_list.filter(
            date_of_birth__month=from_date.month, date_of_birth__day=from_date.day)))
        next_day = from_date + datetime.timedelta(days=1)
        for day in range(0, days):
            doblist.extend(list(person_list.filter(
                date_of_birth__month=next_day.month, date_of_birth__day=next_day.day, date_of_death__isnull=True)))
            next_day = next_day + datetime.timedelta(days=1)
        for dob in doblist:
            dob.date_of_birth = dob.date_of_birth.replace(
                year=datetime.datetime.today().year)
        return doblist

    def ahead_or_behind(self, received, giving):
        if received > giving:
            return "ahead"
        elif received < giving:
            return "behind"

    def merge_dicts(self, *dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def get_context_data(self, **kwargs):
        context = super(BulletinListView, self).get_context_data(**kwargs)
        messages.info(self.request, '')
        now = datetime.datetime.now()
        today = datetime.datetime.today()
        current_year = datetime.datetime.now().year

        # coming sunday's date
        coming_sunday = self.get_coming_sunday(today)

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
                date=coming_sunday)[:1].get()
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
        max_print_annoucements = int(config.MAX_PRINT_ANNOUCEMENTS)
        context['announcements_print'] = published_announcements[
            :max_print_annoucements]
        context['more_annoucements_online_count'] = published_announcements.count(
        ) - max_print_annoucements

        context['theme'] = {'this_year_theme': config.THIS_YEAR_THEME,
                            'this_year_theme_verse': config.THIS_YEAR_THEME_VERSE,
                            'this_year_theme_year': config.THIS_YEAR_THEME_YEAR}

        all_birthdays = Profile.objects.exclude(date_of_birth=None)
        context['birthdays'] = self.get_upcoming_birthdays(all_birthdays, 7)
        context['birthdays_after_coming_sunday'] = self.get_upcoming_birthdays(
            all_birthdays, 7, coming_sunday)

        building_fund_received_ytd = None
        try:
            building_fund_received_ytd = DataPoint.objects.filter(
                date__year=current_year, dataseries__name__exact="Building Fund Weekly Collection").aggregate(Sum('value')).values()[0]
        except DataPoint.DoesNotExist:
            building_fund_received_ytd = None
        context['building_fund_received_ytd'] = building_fund_received_ytd

        building_fund_received = None
        try:
            building_fund_received = DataPoint.objects.filter(
                dataseries__name__exact="Building Fund Weekly Collection").latest('date')
        except DataPoint.DoesNotExist:
            building_fund_received = None
        context['building_fund_received'] = building_fund_received

        building_fund_pledged_ytd = None
        try:
            building_fund_pledged = DataPoint.objects.filter(
                dataseries__name__exact="Building Fund Pledge").latest('date')
            building_fund_pledged_ytd = building_fund_pledged.value / \
                365 * datetime.datetime.now().timetuple().tm_yday
        except DataPoint.DoesNotExist:
            building_fund_pledged_ytd = None
        context['building_fund_pledged_ytd'] = building_fund_pledged_ytd

        building_goal = None
        try:
            building_goal = DataPoint.objects.filter(
                dataseries__name__exact="Building Fund Goal").latest('date')
        except DataPoint.DoesNotExist:
            building_goal = None
        context['building_goal'] = building_goal.value

        context['ahead_or_behind'] = self.ahead_or_behind(1, 2)
        context['building_pledge_received_difference'] = building_fund_pledged_ytd - \
            building_fund_received_ytd
        context['building_goal_received_difference'] = building_goal.value - \
            building_fund_received_ytd
        context['building_goal_received_percent'] = building_fund_received.value / \
            building_goal.value * 100

        weekly_attendance_nursery = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Nursery)").order_by('-date').annotate(weekly_attendance_nursery=F('value')).values('date', 'weekly_attendance_nursery')
        weekly_attendance_preschoolers = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Preschoolers)").order_by('-date').annotate(weekly_attendance_preschoolers=F('value')).values('date', 'weekly_attendance_preschoolers')
        weekly_attendance_childrens_church = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Children\'s Church)").order_by('-date').annotate(weekly_attendance_childrens_church=F('value')).values('date', 'weekly_attendance_childrens_church')
        weekly_attendance_chinese = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Chinese)").order_by('-date').annotate(weekly_attendance_chinese=F('value')).values('date', 'weekly_attendance_chinese')
        weekly_attendance_english = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (English)").order_by('-date').annotate(weekly_attendance_english=F('value')).values('date', 'weekly_attendance_english')
        weekly_attendance_all = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service").all()

        weekly_attendance = DataPoint.objects.filter(dataseries__name__contains="Sunday Morning Service").values('date').order_by('-date').annotate(
            weekly_attendance_nursery=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Nursery)', then='value'))),
            weekly_attendance_preschoolers=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Preschoolers)', then='value'))),
            weekly_attendance_childrens_church=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Children\'s Church)', then='value'))),
            weekly_attendance_chinese=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Chinese)', then='value'))),
            weekly_attendance_english=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (English)', then='value'))),
            total_attendance=Sum('value')
        )[:12]

        context['weekly_attendance'] = weekly_attendance
        context['latest_weekly_attendance'] = weekly_attendance[:1]

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


class BulletinPrintView(StaffRequiredMixin, BulletinListView):
    template_name = 'newswire/cp/bulletin_print.html'


class BulletinPdfView(PdfResponseMixin, BulletinListView):
    template_name = 'newswire/cp/bulletin_pdf.html'

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data()
        template = self.get_template_names()[0]
        html_string = render_to_string(template, context)
        rendered_html = HTML(string=html_string)
        pdf_file = rendered_html.write_pdf(stylesheets=[CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/bootstrap.min.css'), CSS(
            settings.BASE_DIR + '/newswire/static/newswire/cp/css/font-awesome.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/gbm_bulletin_pdf.css')])
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="gbm_bulletin.pdf"'
        return response


class OrderOfServiceList(StaffRequiredMixin, ListView):
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


class OrderOfServiceCreate(StaffRequiredMixin, CreateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceUpdate(StaffRequiredMixin, UpdateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceDelete(StaffRequiredMixin, DeleteView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    template_name = 'newswire/cp/orderofservice_confirm_delete.html'


class AnnouncementList(StaffRequiredMixin, ListView):
    queryset = Announcement.objects.order_by(
        '-publish_start_date', 'publish_end_date')
    template_name = 'newswire/cp/announcement_list.html'


class AnnouncementCreate(StaffRequiredMixin, CreateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class AnnouncementUpdate(StaffRequiredMixin, UpdateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class AnnouncementDelete(StaffRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    template_name = 'newswire/cp/announcement_confirm_delete.html'


class EventList(StaffRequiredMixin, ListView):
    queryset = Event.objects.order_by('-date_start')
    template_name = 'newswire/cp/event_list.html'


class EventCreate(StaffRequiredMixin, CreateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventUpdate(StaffRequiredMixin, UpdateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventDelete(StaffRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('event_list')
    template_name = 'newswire/cp/event_confirm_delete.html'


class CategoryList(StaffRequiredMixin, ListView):
    queryset = Category.objects.all()
    template_name = 'newswire/cp/category_list.html'


class CategoryCreate(StaffRequiredMixin, CreateView):
    model = Category
    success_url = reverse_lazy('category_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryUpdate(StaffRequiredMixin, UpdateView):
    model = Category
    success_url = reverse_lazy('category_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryDelete(StaffRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category_list')
    template_name = 'newswire/cp/category_confirm_delete.html'


class ProfileList(StaffRequiredMixin, ListView):
    queryset = Profile.objects.all()
    template_name = 'newswire/cp/profile_list.html'


class ProfileCreate(StaffRequiredMixin, CreateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileUpdate(StaffRequiredMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileDelete(StaffRequiredMixin, DeleteView):
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


class DataPointList(SuperUserRequiredMixin, ListView):
    queryset = DataPoint.objects.all()
    template_name = 'newswire/cp/datapoint_list.html'


class DataPointCreate(SuperUserRequiredMixin, CreateView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    form_class = DataPointForm
    template_name = 'newswire/cp/datapoint_form.html'


class DataPointUpdate(SuperUserRequiredMixin, UpdateView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    form_class = DataPointForm
    template_name = 'newswire/cp/datapoint_form.html'


class DataPointDelete(SuperUserRequiredMixin, DeleteView):
    model = DataPoint
    success_url = reverse_lazy('datapoint_list')
    template_name = 'newswire/cp/datapoint_confirm_delete.html'


class AttendanceSummary(StaffRequiredMixin, ListView):
    queryset = DataPoint.objects.filter(
        dataseries__name__contains="Sunday Morning Service").order_by('-date')
    template_name = 'newswire/cp/attendance_summary.html'

    def get_context_data(self, **kwargs):
        context = super(AttendanceSummary, self).get_context_data(**kwargs)
        messages.info(self.request, '')
        now = datetime.datetime.now()
        today = datetime.datetime.today()
        current_year = datetime.datetime.now().year

        weekly_attendance_nursery = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Nursery)").order_by('-date').annotate(weekly_attendance_nursery=F('value')).values('date', 'weekly_attendance_nursery', 'pk')
        weekly_attendance_preschoolers = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Preschoolers)").order_by('-date').annotate(weekly_attendance_preschoolers=F('value')).values('date', 'weekly_attendance_preschoolers')
        weekly_attendance_childrens_church = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Children\'s Church)").order_by('-date').annotate(weekly_attendance_childrens_church=F('value')).values('date', 'weekly_attendance_childrens_church')
        weekly_attendance_chinese = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (Chinese)").order_by('-date').annotate(weekly_attendance_chinese=F('value')).values('date', 'weekly_attendance_chinese')
        weekly_attendance_english = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service (English)").order_by('-date').annotate(weekly_attendance_english=F('value')).values('date', 'weekly_attendance_english')
        weekly_attendance_all = DataPoint.objects.filter(
            dataseries__name__contains="Sunday Morning Service").all()

        weekly_attendance = DataPoint.objects.filter(dataseries__name__contains="Sunday Morning Service").values('date').order_by('-date').annotate(
            weekly_attendance_nursery=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Nursery)', then='value'))),
            weekly_attendance_nursery_id=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Nursery)', then='pk'))),
            weekly_attendance_preschoolers=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Preschoolers)', then='value'))),
            weekly_attendance_childrens_church=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Children\'s Church)', then='value'))),
            weekly_attendance_chinese=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (Chinese)', then='value'))),
            weekly_attendance_english=Sum(Case(When(
                dataseries__name__contains='Sunday Morning Service (English)', then='value'))),
            total_attendance=Sum('value')
        )[:24]

        context['weekly_attendance'] = weekly_attendance
        context['latest_weekly_attendance'] = weekly_attendance[:5]

        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class AttendanceList(StaffRequiredMixin, ListView):
    # Filter for attendance objects
    queryset = DataPoint.objects.filter(
        dataseries__name__contains="Sunday Morning Service").order_by('-date')
    template_name = 'newswire/cp/attendance_list.html'


class AttendanceCreate(StaffRequiredMixin, CreateView):
    model = DataPoint
    success_url = reverse_lazy('attendance_new')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'

    def form_valid(self, form):
        attendance = form.save(commit=False)
        attendance.user = User.objects.get(
            username=self.request.user)  # use your own profile here
        attendance.save()
        return HttpResponseRedirect(self.get_success_url())


class AttendanceUpdate(StaffRequiredMixin, UpdateView):
    model = DataPoint
    success_url = reverse_lazy('attendance_list')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceDelete(StaffRequiredMixin, DeleteView):
    model = DataPoint
    success_url = reverse_lazy('attendance_list')
    template_name = 'newswire/cp/attendance_confirm_delete.html'


class DataSeriesList(SuperUserRequiredMixin, ListView):
    queryset = DataSeries.objects.all()
    template_name = 'newswire/cp/dataseries_list.html'


class DataSeriesCreate(SuperUserRequiredMixin, CreateView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    form_class = DataSeriesForm
    template_name = 'newswire/cp/dataseries_form.html'


class DataSeriesUpdate(SuperUserRequiredMixin, UpdateView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    form_class = DataSeriesForm
    template_name = 'newswire/cp/dataseries_form.html'


class DataSeriesDelete(SuperUserRequiredMixin, DeleteView):
    model = DataSeries
    success_url = reverse_lazy('dataseries_list')
    template_name = 'newswire/cp/dataseries_confirm_delete.html'


class WeeklyVerseList(StaffRequiredMixin, ListView):
    queryset = WeeklyVerse.objects.all()
    template_name = 'newswire/cp/weeklyverse_list.html'


class WeeklyVerseCreate(StaffRequiredMixin, CreateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseUpdate(StaffRequiredMixin, UpdateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseDelete(StaffRequiredMixin, DeleteView):
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


class RsvpListView(StaffRequiredMixin, ListView):

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


class RsvpListViewRaw(StaffRequiredMixin, ListView):

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


class ControlPanelHomeView(StaffRequiredMixin, ListView):

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
