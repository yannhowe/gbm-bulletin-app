from django.conf.urls import include, url
from . import views
from .views import BulletinHomePageView, ProfileUpdateView, ProfileDetailView, RsvpUpdateView, RsvpListView, RsvpListViewRaw
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^bulletin/$', BulletinHomePageView.as_view(), name='home'),
    url(r'^bulletin/rsvp/update/$',
        login_required(RsvpUpdateView.as_view()), name='update-rsvp'),
    url(r'^bulletin/send/bulletin/',
        login_required(views.send_bulletin), name='send-bulletin'),
    url(r'^accounts/profile/update/$',
        login_required(ProfileUpdateView.as_view()), name='profile-update'),
    url(r'^accounts/profile/$',
        login_required(ProfileDetailView.as_view()), name='profile-detail'),
)
