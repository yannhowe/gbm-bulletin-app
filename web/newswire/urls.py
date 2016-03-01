from django.conf.urls import url
from . import views
from .views import HomePageView, ProfileUpdateView, ProfileDetailView
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^accounts/profile/update/$',
        login_required(ProfileUpdateView.as_view()), name='profile-update'),
    url(r'^accounts/profile/$',
        login_required(ProfileDetailView.as_view()), name='profile-detail'),
)
