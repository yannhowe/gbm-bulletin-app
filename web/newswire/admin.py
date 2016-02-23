
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionModelAdmin, ImportExportModelAdmin
from django.contrib import admin
from .models import Post, Category, Setting, WeeklySummary, ReadPost, Event, OrderOfService, Unsubscription

from django.forms import ModelForm,TextInput,DateInput
from suit.widgets import EnclosedInput, SuitDateWidget, SuitSplitDateTimeWidget

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = {'title', 'body', 'publish_start_date',
                  'publish_end_date', 'category', 'link', 'hidden', 'contact'}
        widgets = {
            'publish_start_date': SuitDateWidget,
            'publish_end_date': SuitDateWidget,
        }


class PostResource(resources.ModelResource):

    class Meta:
        model = Post


class PostAdmin(ImportExportModelAdmin):
    form = PostForm
    resource_class = PostResource
    pass


admin.site.register(Post, PostAdmin)


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


class ReadPostResource(resources.ModelResource):

    class Meta:
        model = ReadPost


class ReadPostAdmin(ImportExportModelAdmin):
    resource_class = ReadPostResource
    pass

admin.site.register(ReadPost, ReadPostAdmin)


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
