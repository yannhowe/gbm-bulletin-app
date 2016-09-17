from django.conf.urls import include, url
from . import views
from .views import BulletinHomePageView, ProfileDetailFrontEndView, ProfileUpdateFrontEndView, RsvpUpdateView, RsvpListView, RsvpListViewRaw, AttendanceCreateFrontEnd, AnnouncementCreateFrontEnd
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^bulletin/$', BulletinHomePageView.as_view(), name='home'),
    url(r'^bulletin/rsvp/update/$',
        login_required(RsvpUpdateView.as_view()), name='update-rsvp'),
    url(r'^bulletin/send/bulletin/',
        login_required(views.send_bulletin), name='send-bulletin'),
    url(r'^accounts/profile/update/$',
        login_required(ProfileUpdateFrontEndView.as_view()), name='profile_front_end_update'),
    url(r'^accounts/profile/$',
        login_required(ProfileDetailFrontEndView.as_view()), name='profile_front_end_detail'),

    url(r'^bulletin/submit/attendance/$',
        login_required(AttendanceCreateFrontEnd.as_view()), name='attendance_front_end_new'),

    url(r'^bulletin/submit/announcement/$',
        login_required(AnnouncementCreateFrontEnd.as_view()), name='announcement_front_end_new'),
)
