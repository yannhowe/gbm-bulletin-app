
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionModelAdmin, ImportExportModelAdmin
from django.contrib import admin
from .models import Announcement, Category, Setting, WeeklySummary, ReadAnnouncement, Event, Signup, OrderOfService, Unsubscription

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
