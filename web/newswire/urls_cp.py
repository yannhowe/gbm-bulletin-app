from django.conf.urls import url
from . import views
from .views import ProfileUpdateView, ProfileDetailView, RsvpUpdateView, RsvpListView, RsvpListViewRaw, PeopleDirectoryView, PeopleSummaryView, ControlPanelHomeView, OrderOfServiceList, OrderOfServiceUpdate
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^$',
        login_required(ControlPanelHomeView.as_view()), name='cp-home'),
    url(r'^rsvp/list/$',
        login_required(RsvpListView.as_view()), name='cp-rsvp-list'),
    url(r'^rsvp/list/raw$',
        login_required(RsvpListViewRaw.as_view()), name='cp-rsvp-list-raw'),


    url(r'^people/$', PeopleSummaryView.as_view(), name='cp-people-summary'),
    url(r'^people/directory/$', PeopleDirectoryView.as_view(),
        name='cp-people-directory'),

    url(r'^bulletin/$', ControlPanelHomeView.as_view(), name='cp-bulletin-home'),

    # OrderOfService
    url(r'^bulletin/orderofservice/$',
        views.OrderOfServiceList.as_view(), name='orderofservice_list'),
    url(r'^bulletin/orderofservice/new$',
        views.OrderOfServiceCreate.as_view(), name='orderofservice_new'),
    url(r'^bulletin/orderofservice/edit/(?P<pk>\d+)$',
        views.OrderOfServiceUpdate.as_view(), name='orderofservice_edit'),
    url(r'^bulletin/orderofservice/delete/(?P<pk>\d+)$',
        views.OrderOfServiceDelete.as_view(), name='orderofservice_delete'),

    # Announcement
    url(r'^bulletin/announcement/$',
        views.AnnouncementList.as_view(), name='announcement_list'),
    url(r'^bulletin/announcement/new$',
        views.AnnouncementCreate.as_view(), name='announcement_new'),
    url(r'^bulletin/announcement/edit/(?P<pk>\d+)$',
        views.AnnouncementUpdate.as_view(), name='announcement_edit'),
    url(r'^bulletin/announcement/delete/(?P<pk>\d+)$',
        views.AnnouncementDelete.as_view(), name='announcement_delete'),
)
