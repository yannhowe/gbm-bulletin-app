from django.conf.urls import url
from . import views
from .views import ProfileList, ProfileCreate, ProfileUpdate, ProfileDelete, RsvpUpdateView, RsvpListView, RsvpListViewRaw, ControlPanelHomeView, OrderOfServiceList, OrderOfServiceUpdate
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^$',
        login_required(ControlPanelHomeView.as_view()), name='cp_home'),
    url(r'^rsvp/list/$',
        login_required(RsvpListView.as_view()), name='rsvp_list'),
    url(r'^rsvp/list/raw$',
        login_required(RsvpListViewRaw.as_view()), name='rsvp_list_raw'),
    url(r'^bulletin/$', ControlPanelHomeView.as_view(), name='cp_bulletin_home'),

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

    # Category
    url(r'^bulletin/category/$',
        views.CategoryList.as_view(), name='category_list'),
    url(r'^bulletin/category/new$',
        views.CategoryCreate.as_view(), name='category_new'),
    url(r'^bulletin/category/edit/(?P<pk>\d+)$',
        views.CategoryUpdate.as_view(), name='category_edit'),
    url(r'^bulletin/category/delete/(?P<pk>\d+)$',
        views.CategoryDelete.as_view(), name='category_delete'),

    # WeeklySummary
    url(r'^bulletin/weeklysummary/$',
        views.WeeklySummaryList.as_view(), name='weeklysummary_list'),
    url(r'^bulletin/weeklysummary/new$',
        views.WeeklySummaryCreate.as_view(), name='weeklysummary_new'),
    url(r'^bulletin/weeklysummary/edit/(?P<pk>\d+)$',
        views.WeeklySummaryUpdate.as_view(), name='weeklysummary_edit'),
    url(r'^bulletin/weeklysummary/delete/(?P<pk>\d+)$',
        views.WeeklySummaryDelete.as_view(), name='weeklysummary_delete'),

    # Event
    url(r'^bulletin/event/$',
        views.EventList.as_view(), name='event_list'),
    url(r'^bulletin/event/new$',
        views.EventCreate.as_view(), name='event_new'),
    url(r'^bulletin/event/edit/(?P<pk>\d+)$',
        views.EventUpdate.as_view(), name='event_edit'),
    url(r'^bulletin/event/delete/(?P<pk>\d+)$',
        views.EventDelete.as_view(), name='event_delete'),


    # Profile
    url(r'^people/summary/$',
        views.ProfileList.as_view(), name='profile_summary'),

    url(r'^people/$',
        views.ProfileList.as_view(), name='profile_list'),
    url(r'^people/new$',
        views.ProfileCreate.as_view(), name='profile_new'),
    url(r'^people/edit/(?P<pk>\d+)$',
        views.ProfileUpdate.as_view(), name='profile_edit'),
    url(r'^people/delete/(?P<pk>\d+)$',
        views.ProfileDelete.as_view(), name='profile_delete'),


    # DataPoint
    url(r'^datapoint/summary/$',
        views.DataPointList.as_view(), name='datapoint_summary'),

    url(r'^datapoint/$',
        views.DataPointList.as_view(), name='datapoint_list'),
    url(r'^datapoint/new$',
        views.DataPointCreate.as_view(), name='datapoint_new'),
    url(r'^datapoint/edit/(?P<pk>\d+)$',
        views.DataPointUpdate.as_view(), name='datapoint_edit'),
    url(r'^datapoint/delete/(?P<pk>\d+)$',
        views.DataPointDelete.as_view(), name='datapoint_delete'),
)
