from django.contrib import admin

# Register your models here.
from labeling.models import LabelImage, InspectImage, OutsourcingLabeling


# class LabelImageAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'image', 'date_labeled')


# class InspectImageAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'image', 'date_inspected')

@admin.register(OutsourcingLabeling)
class OutsourcingLabelingAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'item']


admin.site.register(LabelImage)
admin.site.register(InspectImage)
