from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Button
from crispy_forms.bootstrap import FormActions, PrependedText, InlineRadios

from django.contrib.auth.models import User
from django import forms
from models import OrderOfService, Announcement, Category, WeeklySummary, Event, Profile, DataPoint, DataSeries, WeeklyVerse


class ProfileFormFrontEnd(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileFormFrontEnd, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Update'),
                HTML(
                    """<a href="{% url 'profile_front_end_detail' %}" class="btn btn-secondary" role="button">Cancel</a>"""),
            ))


class ProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['member'].label = "Account to Attach this Profile to"
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field(
                'first_name',
                'last_name',
            ),
            Field('member', css_class='select_user_to_attach'),
            PrependedText('email', '<i class="fa fa-envelope"></i>',
                          type="email"),
            Field(
                'prefered_name',
                'maiden_name',
            ),
            InlineRadios('gender'),
            PrependedText('date_of_birth', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_marriage', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_baptism', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_death', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('mobile_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            PrependedText('home_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            Field(
                'address_block',
                'address_street',
                'address_unit',
                'country',
                'postal_code',
                'is_regular',
                'is_member'
            ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "profile_list" %}>Cancel</a>'),
            )
        )
        gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')))

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'member', 'email', 'prefered_name', 'maiden_name', 'gender', 'date_of_birth', 'date_of_marriage', 'date_of_baptism',
                  'date_of_death', 'mobile_number', 'home_number', 'address_block', 'address_street', 'address_unit', 'country', 'postal_code', 'is_regular', 'is_member']


class DataPointForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(DataPointForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "datapoint_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = DataPoint
        fields = '__all__'


class AttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "attendance_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = DataPoint
        fields = '__all__'


class DataSeriesForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(DataSeriesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "dataseries_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = DataSeries
        fields = '__all__'


class WeeklyVerseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(WeeklyVerseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "weeklyverse_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = WeeklyVerse
        fields = '__all__'


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
