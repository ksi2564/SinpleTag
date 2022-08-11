from django.contrib import admin

# Register your models here.
from labeling.models import LabelImage, InspectImage


class LabelImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image', 'top_category', 'date_labeled')


class InspectImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image', 'top_category', 'date_inspected')


admin.site.register(LabelImage, LabelImageAdmin)
admin.site.register(InspectImage, InspectImageAdmin)
