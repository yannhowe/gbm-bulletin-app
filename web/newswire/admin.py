
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionModelAdmin, ImportExportModelAdmin
from django.contrib import admin
from .models import Announcement, Category, Setting, WeeklySummary, ReadAnnouncement, Event, Signup, OrderOfService, Unsubscription, Profile, Relationship, DataPoint, DataSeries, Group

from django.forms import ModelForm, TextInput, DateInput
from suit.widgets import EnclosedInput, SuitDateWidget, SuitSplitDateTimeWidget


class AnnouncementForm(ModelForm):

    class Meta:
        model = Announcement
        fields = {'title', 'body', 'publish_start_date',
                  'publish_end_date', 'category', 'link', 'hidden', 'contact'}
        widgets = {
            #'publish_start_date': SuitDateWidget,
            #'publish_end_date': SuitDateWidget,
        }


class AnnouncementResource(resources.ModelResource):

    class Meta:
        model = Announcement


class AnnouncementAdmin(ImportExportModelAdmin):
    form = AnnouncementForm
    resource_class = AnnouncementResource
    ordering = ('-publish_start_date',)

    pass


admin.site.register(Announcement, AnnouncementAdmin)


class CategoryResource(resources.ModelResource):

    class Meta:
        model = Category


class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    pass

admin.site.register(Category, CategoryAdmin)


class SettingResource(resources.ModelResource):

    class Meta:
        model = Setting


class SettingAdmin(ImportExportModelAdmin):
    resource_class = SettingResource
    pass

admin.site.register(Setting, SettingAdmin)


class WeeklySummaryResource(resources.ModelResource):

    class Meta:
        model = WeeklySummary


class WeeklySummaryAdmin(ImportExportModelAdmin):
    resource_class = WeeklySummaryResource
    pass

admin.site.register(WeeklySummary, WeeklySummaryAdmin)


class ReadAnnouncementResource(resources.ModelResource):

    class Meta:
        model = ReadAnnouncement


class ReadAnnouncementAdmin(ImportExportModelAdmin):
    resource_class = ReadAnnouncementResource
    pass

admin.site.register(ReadAnnouncement, ReadAnnouncementAdmin)


class EventResource(resources.ModelResource):

    class Meta:
        model = Event


class EventForm(ModelForm):

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date_start': DateInput,
        }


class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource
    pass

admin.site.register(Event, EventAdmin)


class SignupResource(resources.ModelResource):

    class Meta:
        model = Signup


class SignupAdmin(ImportExportModelAdmin):
    resource_class = SignupResource
    pass

admin.site.register(Signup, SignupAdmin)


class OrderOfServiceResource(resources.ModelResource):

    class Meta:
        model = OrderOfService


class OrderOfServiceAdmin(ImportExportModelAdmin):
    resource_class = OrderOfServiceResource
    pass

admin.site.register(OrderOfService, OrderOfServiceAdmin)


class UnsubscriptionResource(resources.ModelResource):

    class Meta:
        model = Unsubscription


class UnsubscriptionAdmin(ImportExportModelAdmin):
    resource_class = UnsubscriptionResource
    pass

admin.site.register(Unsubscription, UnsubscriptionAdmin)


class RelationshipResource(resources.ModelResource):

    class Meta:
        model = Relationship


class RelationshipForm(ModelForm):

    class Meta:
        model = Relationship
        fields = '__all__'


class RelationshipAdmin(ImportExportModelAdmin):
    resource_class = RelationshipResource
    pass

admin.site.register(Relationship, RelationshipAdmin)


class ProfileResource(resources.ModelResource):

    class Meta:
        model = Profile


class ProfileForm(ModelForm):

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    pass

admin.site.register(Profile, ProfileAdmin)


class GroupResource(resources.ModelResource):

    class Meta:
        model = Group


class GroupForm(ModelForm):

    class Meta:
        model = Group
        fields = '__all__'


class GroupAdmin(ImportExportModelAdmin):
    resource_class = GroupResource
    pass

admin.site.register(Group, GroupAdmin)


class DataPointResource(resources.ModelResource):

    class Meta:
        model = DataPoint


class DataPointForm(ModelForm):

    class Meta:
        model = DataPoint
        fields = '__all__'


class DataPointAdmin(ImportExportModelAdmin):
    resource_class = DataPointResource
    pass

admin.site.register(DataPoint, DataPointAdmin)


class DataSeriesResource(resources.ModelResource):

    class Meta:
        model = DataSeries


class DataSeriesForm(ModelForm):

    class Meta:
        model = DataSeries
        fields = '__all__'


class DataSeriesAdmin(ImportExportModelAdmin):
    resource_class = DataSeriesResource
    pass

admin.site.register(DataSeries, DataSeriesAdmin)
