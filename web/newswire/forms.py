from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Button
from crispy_forms.bootstrap import FormActions, PrependedText

from django.contrib.auth.models import User
from django import forms
from models import OrderOfService, Announcement


class ProfileForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Update'),
                HTML(
                    """<a href="{% url 'profile-detail' %}" class="btn btn-secondary" role="button">Cancel</a>"""),
            ))


class OrderOfServiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrderOfServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('service_name'),
            PrependedText('date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            Field('text'),

            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "orderofservice_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = OrderOfService
        fields = ['date', 'text', 'service_name']


class AnnouncementForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('title', 'body'),
            PrependedText('publish_start_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            PrependedText('publish_end_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            Field('category', 'link', ),
            Field('hidden', title="Hide this Announcement"),
            Field('contact'),

            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "announcement_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Announcement
        fields = ['title', 'body', 'publish_start_date', 'publish_end_date','category', 'link','hidden', 'contact',]
