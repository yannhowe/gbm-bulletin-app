from django.conf.urls import url
from . import views
from .views import HomePageView, ProfileUpdateView, ProfileDetailView, RsvpUpdateView, RsvpListView
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^accounts/profile/update/$',
        login_required(ProfileUpdateView.as_view()), name='profile-update'),
    url(r'^accounts/profile/$',
        login_required(ProfileDetailView.as_view()), name='profile-detail'),
    url(r'^rsvp/update/$',
        login_required(RsvpUpdateView.as_view()), name='update-rsvp'),
    url(r'^rsvp/list/$',
        login_required(RsvpListView.as_view()), name='list-rsvp'),
    url(r'^send/bulletin/', login_required(views.send_bulletin), name='send-bulletin'),
)
