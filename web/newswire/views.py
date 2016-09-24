# -*- coding: utf-8 -*-
from .forms import ProfileForm, ProfileFormFrontEnd, OrderOfServiceForm, AnnouncementForm, CategoryForm, EventForm, AttendanceForm, WeeklyVerseForm, AttendanceForm, AttendanceFormFrontEnd, AnnouncementFormFrontEnd, BuildingFundCollectionForm, BuildingFundYearPledgeForm, BuildingFundYearGoalForm
from .models import Announcement, Category, OrderOfService, Announcement, Event, ReadAnnouncement, Setting, Unsubscription, Signup, Profile, Relationship, WeeklyVerse, SundayAttendance, BuildingFundCollection, BuildingFundYearPledge, BuildingFundYearGoal
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
from django.template import Context
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


now = datetime.datetime.now()
today = datetime.datetime.today()
current_year = datetime.datetime.now().year


def get_upcoming_birthdays(person_list, days, from_date=datetime.datetime.today()):
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


def get_coming_sunday(date):
    # coming sunday's date
    coming_sunday = date
    while coming_sunday.weekday() != 6:
        coming_sunday += datetime.timedelta(1)
    return coming_sunday

coming_sunday = get_coming_sunday(today)


def ahead_or_behind(collection, goal):
    if collection > goal:
        return "ahead"
    elif collection < goal:
        return "behind"


def updated_or_not(object_date, expected_date):
    try:
        a = object_date.date()
    except Exception as e:
        a = object_date
    try:
        b = expected_date.date()
    except Exception as e:
        b = expected_date
    if a == b:
        return True
    else:
        return False


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


def _template_email_convenience(to, fail_silently=False, **kwargs):
    to = [formataddr(recipient) for recipient in to]
    final_kwargs = {'from_email': settings.SERVER_EMAIL}
    final_kwargs.update(kwargs)

    message = template_email(to=to, **final_kwargs)
    if settings.EMAIL_SUBJECT_PREFIX:
        message.subject = (
            settings.EMAIL_SUBJECT_PREFIX + message.subject)
    message.send(fail_silently=fail_silently)


def template_mail_managers(**kwargs):
    return _template_email_convenience(to=settings.MANAGERS, **kwargs)


def template_mail_admins(**kwargs):
    return _template_email_convenience(to=settings.ADMINS, **kwargs)


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


class NeedsReviewMixin(object):

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.submitter = User.objects.get(
            username=self.request.user)
        submission.approver = None
        submission.under_review = True
        submission.save()
        # TODO Email admins that new announcement has been submitted for review
        message = template_email(
            template_name='emails/new_item_for_review',
            to=config.UNDER_REVIEW_ADMINS.split()
        )
        message.send()
        return HttpResponseRedirect(self.success_url)


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


class UnderReviewListView(ListView):
    model = Announcement
    template_name = 'newswire/cp/under_review_list.html'

    def get_context_data(self, **kwargs):
        context = super(UnderReviewListView, self).get_context_data(**kwargs)

        try:
            announcements = Announcement.objects.all()
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(
                publish_start_date__lte=now, publish_end_date__gte=now, under_review=True)
            announcements_under_review_count = announcements_under_review.count()
            context['announcements_under_review'] = announcements_under_review
            context[
                'announcements_under_review_count'] = announcements_under_review_count

        try:
            sunday_attendance = SundayAttendance.objects.all()
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(
                under_review=True)
            sunday_attendance_under_review_count = sunday_attendance_under_review.count()
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['graph_sunday_attendance'] = sunday_attendance.order_by(
                '-date')[:25]
            context['recent_sunday_attendance'] = sunday_attendance.order_by(
                '-date')[:4]
            context[
                'sunday_attendance_under_review_count'] = sunday_attendance_under_review_count

        if sunday_attendance and announcements:
            context['total_under_review_count'] = announcements_under_review_count + \
                sunday_attendance_under_review_count

        return context


class BulletinListView(ListView):
    model = Announcement
    template_name = 'newswire/home.html'

    def get_context_data(self, **kwargs):
        context = super(BulletinListView, self).get_context_data(**kwargs)

        try:
            order_of_service = OrderOfService.objects.all()
        except OrderOfService.DoesNotExist:
            order_of_service = None

        if order_of_service:
            try:
                coming_sunday_order_of_service = order_of_service.order_by(
                    'date').filter(date=coming_sunday)[:1].get()
            except OrderOfService.DoesNotExist:
                coming_sunday_order_of_service = None

        if coming_sunday_order_of_service:
            context[
                'coming_sunday_order_of_service'] = coming_sunday_order_of_service
            context['orderofservice_updated_or_not'] = updated_or_not(
                coming_sunday_order_of_service.date, coming_sunday)

        active_announcements = Announcement.objects.filter(
            publish_start_date__lte=now).filter(publish_end_date__gte=now)
        unread_active_announcements = Announcement.objects.exclude(
            readannouncement__announcement__id__in=active_announcements)
        published_announcements = unread_active_announcements.filter(publish_start_date__lte=today, publish_end_date__gte=today, hidden=False, under_review=False).extra(
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
        context['birthdays'] = get_upcoming_birthdays(all_birthdays, 7)
        context['birthdays_after_coming_sunday'] = get_upcoming_birthdays(
            all_birthdays, 7, coming_sunday)

        SundayAttendanceApproved = SundayAttendance.objects.exclude(
            under_review=True)
        context['graph_sunday_attendance'] = SundayAttendanceApproved.order_by(
            '-date')[:25]
        context['recent_sunday_attendance'] = SundayAttendanceApproved.order_by(
            '-date')[:4]
        context['latest_sunday_attendance'] = SundayAttendanceApproved.order_by(
            '-date')[:1]

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

        try:
            building_fund_year_goal = BuildingFundYearGoal.objects.all()
        except BuildingFundYearGoal.DoesNotExist:
            building_fund_year_goal = None

        try:
            building_fund_year_pledge = BuildingFundYearPledge.objects.all()
        except BuildingFundYearPledge.DoesNotExist:
            building_fund_year_pledge = None

        try:
            building_fund_collection = BuildingFundCollection.objects.all()
        except BuildingFundCollection.DoesNotExist:
            building_fund_collection = None

        if building_fund_year_goal and building_fund_year_pledge and building_fund_collection:
            building_fund_collection_ytd = building_fund_collection.filter(
                date__year=current_year).aggregate(Sum('amount')).values()[0]
            building_fund_pledged_ytd = building_fund_year_pledge.latest(
                'date').amount / 365 * datetime.datetime.now().timetuple().tm_yday
            building_fund_year_goal = building_fund_year_goal.latest(
                'date').amount
            building_pledge_and_ytd_collection_difference = building_fund_pledged_ytd - \
                building_fund_collection_ytd
            building_goal_and_ytd_collection_difference = building_fund_year_goal - \
                building_fund_collection_ytd
            building_goal_and_ytd_collection_percent = building_fund_collection_ytd / \
                building_fund_year_goal * 100
            ahead_or_behind_goal = ahead_or_behind(
                building_fund_collection_ytd, building_fund_year_goal)

            context['building_fund_collection_latest'] = building_fund_collection.latest(
                'date')
            context['building_fund_collection_ytd'] = building_fund_collection_ytd
            context['building_fund_pledged_ytd'] = building_fund_pledged_ytd
            context['building_fund_year_goal'] = building_fund_year_goal
            context['building_pledge_and_ytd_collection_difference'] = abs(
                building_pledge_and_ytd_collection_difference)
            context['building_goal_and_ytd_collection_difference'] = abs(
                building_goal_and_ytd_collection_difference)
            context[
                'building_goal_and_ytd_collection_percent'] = building_goal_and_ytd_collection_percent
            context['ahead_or_behind'] = ahead_or_behind_goal

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
        filename = coming_sunday.strftime('%Y%m%d') + '_gbm_bulletin.pdf'
        pdf_file = rendered_html.write_pdf(stylesheets=[CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/bootstrap.min.css'), CSS(
            settings.BASE_DIR + '/newswire/static/newswire/cp/css/font-awesome.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/gbm_bulletin_pdf.css')])
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response[
            'Content-Disposition'] = 'filename="{}"'.format(filename)
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
        context['highlight'] = {
            'oos_tip_lines': config.ORDER_OF_SERVICE_TIP_LINES,
            'oos_warning_lines': config.ORDER_OF_SERVICE_WARNING_LINES,
        }

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

    def get_context_data(self, **kwargs):
        context = super(AnnouncementList, self).get_context_data(**kwargs)
        now = datetime.datetime.now()

        try:
            categories = Category.objects.all()
        except Category.DoesNotExist:
            categories = None
        context['categories'] = categories
        return context


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


class UnderReviewFrontEndListView(ListView):
    model = Announcement
    template_name = 'newswire/submissions_under_review.html'

    def get_context_data(self, **kwargs):
        context = super(UnderReviewFrontEndListView,
                        self).get_context_data(**kwargs)

        try:
            announcements = Announcement.objects.filter(
                submitter=self.request.user, publish_end_date__gte=today - datetime.timedelta(days=28))
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(
                under_review=True)
            announcements_approved = announcements.filter(under_review=False)
            context['announcements_under_review'] = announcements_under_review
            context['announcements_approved'] = announcements_approved

        try:
            sunday_attendance = SundayAttendance.objects.filter(
                submitter=self.request.user, date__gte=today - datetime.timedelta(days=28))
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(
                under_review=True)
            sunday_attendance_approved = sunday_attendance.filter(
                under_review=False)
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['sunday_attendance_approved'] = sunday_attendance_approved

        return context


class AnnouncementFrontEndCreate(NeedsReviewMixin, CreateView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    form_class = AnnouncementFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Create Announcement - ',
        'header': 'Announcement Review Form',
        'description': 'Use this to submit announcements for review'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndCreate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementFrontEndUpdate(NeedsReviewMixin, UpdateView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    form_class = AnnouncementFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Update Sunday Announcement - ',
        'header': 'Update Sunday Announcement',
        'description': 'Use this to update announcements'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndUpdate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementFrontEndDelete(DeleteView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    template_name = 'newswire/delete-form.html'
    page = Context({
        'title': 'Delete Sunday Announcement - ',
        'header': 'Delete Sunday Announcement',
        'description': 'Use this to delete announcements'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndDelete,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementDelete(StaffRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    template_name = 'newswire/cp/announcement_confirm_delete.html'


class UnderReviewApproveView(DetailView):

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            the_user = request.user
            response_data = {}
            announcenment = Announcement()

            approval_object_id = request.POST.get('approval_object_id')
            approval_object_type = request.POST.get('approval_object_type')
            something_updated_successfully = False

            if approval_object_type == "announcement":
                try:
                    announcenment = Announcement()
                    announcenment = Announcement.objects.get(
                        pk=approval_object_id)
                    announcenment.under_review = False
                    announcenment.approver = the_user
                    announcenment.save()
                    something_updated_successfully = True
                except:
                    pass

            if approval_object_type == "attendance":
                try:
                    attendance = SundayAttendance()
                    attendance = SundayAttendance.objects.get(
                        pk=approval_object_id)
                    attendance.under_review = False
                    attendance.approver = the_user
                    attendance.save()
                    something_updated_successfully = True
                except:
                    pass

            if something_updated_successfully:
                response_data['approval_object_status'] = "Updated"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                response_data['approval_object_status'] = "Update Failed"
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
    success_url = reverse_lazy('announcement_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryUpdate(StaffRequiredMixin, UpdateView):
    model = Category
    success_url = reverse_lazy('announcement_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryDelete(StaffRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('announcement_list')
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


class AttendanceSummary(StaffRequiredMixin, ListView):
    queryset = SundayAttendance.objects.all()
    template_name = 'newswire/cp/attendance_summary.html'

    def get_context_data(self, **kwargs):
        context = super(AttendanceSummary, self).get_context_data(**kwargs)
        context['graph_sunday_attendance'] = SundayAttendance.objects.order_by(
            '-date')[:25]
        context['recent_sunday_attendance'] = SundayAttendance.objects.order_by(
            '-date')[:4]
        return context


class AttendanceCreate(StaffRequiredMixin,  CreateView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_new')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceUpdate(StaffRequiredMixin, UpdateView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_summary')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceDelete(StaffRequiredMixin, DeleteView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_summary')
    template_name = 'newswire/cp/attendance_confirm_delete.html'


class AttendanceFrontEndCreate(NeedsReviewMixin, CreateView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    form_class = AttendanceFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Create Sunday Attendance - ',
        'header': 'Sunday Attendance Form',
        'description': 'Use this to submit attendance records for review'
    })

    def get_context_data(self, **kwargs):
        context = super(AttendanceFrontEndCreate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AttendanceFrontEndUpdate(NeedsReviewMixin, UpdateView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    form_class = AttendanceFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Update Sunday Attendance - ',
        'header': 'Update Sunday Attendance',
        'description': 'Use this to update attendance records'
    })


class AttendanceFrontEndDelete(DeleteView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    template_name = 'newswire/delete-form.html'
    page = Context({
        'title': 'Delete Sunday Attendance - ',
        'header': 'Delete Sunday Attendance',
        'description': 'Use this to delete attendance records'
    })


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


class BuildingFundList(StaffRequiredMixin, ListView):
    model = BuildingFundCollection
    template_name = 'newswire/cp/buildingfund.html'

    def get_context_data(self, **kwargs):
        context = super(BuildingFundList, self).get_context_data(**kwargs)

        try:
            building_fund_collection = BuildingFundCollection.objects.all()
            context['building_fund_collection'] = building_fund_collection
            context['latest_building_fund_collection'] = BuildingFundCollection.objects.latest(
                'date')
        except BuildingFundCollection.DoesNotExist:
            building_fund_collection = None

        try:
            building_fund_year_pledge = BuildingFundYearPledge.objects.all()
            context['building_fund_year_pledge'] = building_fund_year_pledge
            context['latest_building_fund_year_pledge'] = BuildingFundYearPledge.objects.latest(
                'date')
        except BuildingFundYearPledge.DoesNotExist:
            building_fund_year_pledge = None

        try:
            building_fund_year_goal = BuildingFundYearGoal.objects.all()
            context['building_fund_year_goal'] = building_fund_year_goal
            context['latest_building_fund_year_goal'] = BuildingFundYearGoal.objects.latest(
                'date')
        except BuildingFundYearGoal.DoesNotExist:
            building_fund_year_goal = None

        return context


class BuildingFundCollectionCreate(StaffRequiredMixin, CreateView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundCollectionForm
    template_name = 'newswire/cp/buildingfundcollection_form.html'


class BuildingFundCollectionUpdate(StaffRequiredMixin, UpdateView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundCollectionForm
    template_name = 'newswire/cp/buildingfundcollection_form.html'


class BuildingFundCollectionDelete(StaffRequiredMixin, DeleteView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundcollection_confirm_delete.html'


class BuildingFundYearPledgeCreate(StaffRequiredMixin, CreateView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearPledgeForm
    template_name = 'newswire/cp/buildingfundyearpledge_form.html'


class BuildingFundYearPledgeUpdate(StaffRequiredMixin, UpdateView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearPledgeForm
    template_name = 'newswire/cp/buildingfundyearpledge_form.html'


class BuildingFundYearPledgeDelete(StaffRequiredMixin, DeleteView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundyearpledge_confirm_delete.html'


class BuildingFundYearGoalCreate(StaffRequiredMixin, CreateView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearGoalForm
    template_name = 'newswire/cp/buildingfundyeargoal_form.html'


class BuildingFundYearGoalUpdate(StaffRequiredMixin, UpdateView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearGoalForm
    template_name = 'newswire/cp/buildingfundyeargoal_form.html'


class BuildingFundYearGoalDelete(StaffRequiredMixin, DeleteView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundyeargoal_confirm_delete.html'


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

        context['coming_sunday'] = coming_sunday.date

        try:
            announcements = Announcement.objects.all()
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(
                publish_start_date__lte=now, publish_end_date__gte=now, under_review=True)
            announcements_under_review_count = announcements_under_review.count()
            context['announcements_under_review'] = announcements_under_review
            context[
                'announcements_under_review_count'] = announcements_under_review_count

        try:
            sunday_attendance = SundayAttendance.objects.all()
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(
                under_review=True)
            sunday_attendance_under_review_count = sunday_attendance_under_review.count()
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['graph_sunday_attendance'] = sunday_attendance.order_by(
                '-date')[:25]
            context['recent_sunday_attendance'] = sunday_attendance.order_by(
                '-date')[:4]
            context[
                'sunday_attendance_under_review_count'] = sunday_attendance_under_review_count

        if sunday_attendance and announcements:
            context['total_under_review_count'] = announcements_under_review_count + \
                sunday_attendance_under_review_count

        try:
            context['signups'] = Signup.objects.order_by('event', 'rsvp')
        except Event.DoesNotExist:
            pass

        try:
            order_of_service = OrderOfService.objects.all()
        except OrderOfService.DoesNotExist:
            order_of_service = None

        if order_of_service:
            try:
                coming_sunday_order_of_service = order_of_service.order_by(
                    'date').filter(date=coming_sunday)[:1].get()
            except OrderOfService.DoesNotExist:
                coming_sunday_order_of_service = None

        if coming_sunday_order_of_service:
            context[
                'coming_sunday_order_of_service'] = coming_sunday_order_of_service
            context['orderofservice_updated_or_not'] = updated_or_not(
                coming_sunday_order_of_service.date, coming_sunday.date)
            context['orderofservice_print'] = coming_sunday_order_of_service

        try:
            order_of_service = OrderOfService.objects.all()
        except OrderOfService.DoesNotExist:
            order_of_service = None

        active_announcements = Announcement.objects.filter(
            publish_start_date__lte=now, publish_end_date__gte=now, under_review=False)
        context['announcements'] = active_announcements

        all_birthdays = Profile.objects.exclude(date_of_birth=None)
        context['birthdays'] = get_upcoming_birthdays(all_birthdays, 7)
        context['birthdays_after_coming_sunday'] = get_upcoming_birthdays(
            all_birthdays, 7, coming_sunday)

        try:
            latest_weeklyverse = WeeklyVerse.objects.latest('date')
        except WeeklyVerse.DoesNotExist:
            latest_weeklyverse = None

        if latest_weeklyverse:
            context['weeklyverse'] = latest_weeklyverse
            context['weeklyverse_updated_or_not'] = updated_or_not(
                latest_weeklyverse.date, today.date)

        try:
            active_events = Event.objects.filter(
                Q(date_end__gte=now) | Q(date_start__gte=now))
        except Event.DoesNotExist:
            active_events = None
        context['events'] = active_events.extra(
            order_by=['date_start'])

        try:
            building_fund_year_goal = BuildingFundYearGoal.objects.all()
        except BuildingFundYearGoal.DoesNotExist:
            building_fund_year_goal = None

        try:
            building_fund_year_pledge = BuildingFundYearPledge.objects.all()
        except BuildingFundYearPledge.DoesNotExist:
            building_fund_year_pledge = None

        try:
            building_fund_collection = BuildingFundCollection.objects.all()
        except BuildingFundCollection.DoesNotExist:
            building_fund_collection = None

        if building_fund_year_goal and building_fund_year_pledge and building_fund_collection:
            building_fund_collection_ytd = building_fund_collection.filter(
                date__year=current_year).aggregate(Sum('amount')).values()[0]
            building_fund_pledged_ytd = building_fund_year_pledge.latest(
                'date').amount / 365 * datetime.datetime.now().timetuple().tm_yday
            building_fund_year_goal = building_fund_year_goal.latest(
                'date').amount
            building_pledge_and_ytd_collection_difference = building_fund_pledged_ytd - \
                building_fund_collection_ytd
            building_goal_and_ytd_collection_difference = building_fund_year_goal - \
                building_fund_collection_ytd
            building_goal_and_ytd_collection_percent = building_fund_collection_ytd / \
                building_fund_year_goal * 100
            ahead_or_behind_goal = ahead_or_behind(
                building_fund_collection_ytd, building_fund_year_goal)

            context['building_fund_collection_latest'] = building_fund_collection.latest(
                'date')
            context['building_fund_collection_ytd'] = building_fund_collection_ytd
            context['building_fund_pledged_ytd'] = building_fund_pledged_ytd
            context['building_fund_year_goal'] = building_fund_year_goal
            context['building_pledge_and_ytd_collection_difference'] = abs(
                building_pledge_and_ytd_collection_difference)
            context['building_goal_and_ytd_collection_difference'] = abs(
                building_goal_and_ytd_collection_difference)
            context[
                'building_goal_and_ytd_collection_percent'] = building_goal_and_ytd_collection_percent
            context['ahead_or_behind'] = ahead_or_behind_goal

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
