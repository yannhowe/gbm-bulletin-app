# -*- coding: utf-8 -*-
from .forms import ProfileUpdateForm, RsvpUpdateForm
from .models import Post, Category, WeeklySummary, OrderOfService, Event, ReadPost, Setting, Unsubscription, Signup
from datetime import datetime
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template, get_template
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, FormView
from email.Utils import formataddr
import os, json


class HomePageView(ListView):
    model = Post
    template_name = 'newswire/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        messages.info(self.request, '')
        now = datetime.now()
        upcoming_service = None
        try:
            upcoming_service = OrderOfService.objects.filter(
                date__gt=datetime.now())[:1].get()
        except OrderOfService.DoesNotExist:
            upcoming_service = None
        context['orderofservice'] = upcoming_service
        active_posts = Post.objects.filter(
            publish_start_date__lte=now).filter(publish_end_date__gte=now)
        unread_active_posts = Post.objects.exclude(
            readpost__post__id__in=active_posts)
        context['posts'] = unread_active_posts.extra(
            order_by=['-publish_start_date'])
        try:
            latest_weeklysummary = WeeklySummary.objects.latest('date')
        except WeeklySummary.DoesNotExist:
            latest_weeklysummary = None
        context['weeklysummary'] = latest_weeklysummary
        context['events'] = Event.objects.extra(
            order_by=['date_start'])
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class ProfileDetailView(DetailView):
    template_name = 'newswire/profile-detail.html'

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class ProfileUpdateView(UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'newswire/profile-update.html'

    def get_success_url(self):
        return reverse('profile-detail')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class RsvpUpdateView(DetailView):

    model = Signup

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            the_user = request.user
            the_rsvp = request.POST.get('the_rsvp')
            the_event = Event.objects.get(pk=request.POST.get('the_event'))
            response_data = {}

            signup = Signup(user=the_user, event=the_event, rsvp=the_rsvp)
            signup.save()

            response_data['result'] = 'Create RSVP successful!'
            response_data['the_user'] = signup.user.pk
            response_data['the_rsvp'] = signup.event.pk
            response_data['the_event'] = signup.pk

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
