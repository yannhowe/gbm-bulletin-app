from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Button
from crispy_forms.bootstrap import FormActions, PrependedText

from django.contrib.auth.models import User
from django import forms
from models import OrderOfService, Announcement, Category, WeeklySummary, Event


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
            PrependedText('date', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
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
            PrependedText(
                'publish_start_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            PrependedText(
                'publish_end_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
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
        fields = ['title', 'body', 'publish_start_date',
                  'publish_end_date', 'category', 'link', 'hidden', 'contact', ]


class CategoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('name', 'description'),
            Field('color', css_class="color-picker-1"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "category_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Category
        fields = ['name', 'description', 'color']


class WeeklySummaryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WeeklySummaryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            PrependedText('date', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('attendance', 'tithe_amt', 'building_amt', 'building_pledge_form_amt',
                  'monthly_loan_servicing_amt', 'c1_title', 'c1_amt', 'c2_title', 'c2_amt', 'c3_title', 'c3_amt'),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "weeklysummary_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = WeeklySummary
        fields = ['date', 'attendance', 'tithe_amt', 'building_amt', 'building_pledge_form_amt',
                  'monthly_loan_servicing_amt', 'c1_title', 'c1_amt', 'c2_title', 'c2_amt', 'c3_title', 'c3_amt']


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('title'),
            PrependedText('date_start', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_end', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('track_rsvp', title="Enable RSVP"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "event_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Event
        fields = ['title', 'date_start', 'date_end', 'track_rsvp']
