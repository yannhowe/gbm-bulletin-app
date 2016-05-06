from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from crispy_forms.bootstrap import FormActions

from django.contrib.auth.models import User
from django import forms
from members.models import Detail, Relationship


class ProfileUpdateForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Update'),
                HTML(
                    """<a href="{% url 'profile-detail' %}" class="btn btn-secondary" role="button">Cancel</a>"""),
            ))


DETAIL_FORM_PREFIX = 'det'


class DetailForm(forms.ModelForm):

    class Meta:
        model = Detail
        fields = [
            'member', 'gender', 'date_record_created', 'date_of_birth', 'date_of_marriage', 'date_of_baptism',
            'date_of_death', 'mobile_number', 'home_number', 'address_block',
            'address_street', 'address_unit', 'country', 'postal_code',
            'is_regular', 'is_member']

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = DETAIL_FORM_PREFIX
        super(DetailForm, self).__init__(*args, **kwargs)
