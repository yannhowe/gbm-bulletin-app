# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.utils import timezone
from django.core.files.storage import default_storage

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic.list import ListView

from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from django.contrib.auth.models import User
from datetime import datetime

from .models import Post, Category, WeeklySummary, OrderOfService, Event, ReadPost, Setting, Unsubscription

from django.views.generic.edit import FormView


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
        context['events'] = Event.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


def post_list(request):
    selected_category_list = ['Chinese Ministry', 'Children\'s Ministry']
    posts = Post.objects.order_by('publish_start_date')
    return render(request, 'newswire/home.html', {'posts': posts})


def get_context_data(self, **kwargs):
    context = super(HomePageView, self).get_context_data(**kwargs)
    messages.info(self.request, 'This is a demo of a message.')
    return context
