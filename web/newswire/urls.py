from django.conf.urls import url
from . import views
from .views import HomePageView

urlpatterns = (
    url(r'^$', HomePageView.as_view(), name='home'),
)
