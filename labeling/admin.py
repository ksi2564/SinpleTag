from django.contrib import admin

# Register your models here.
from labeling.models import LabelImage, InspectImage, OutsourcingLabeling, InspectOutsourcingLabeling


@admin.register(OutsourcingLabeling)
class OutsourcingLabelingAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'item']
    list_filter = ('item',)


@admin.register(InspectOutsourcingLabeling)
class InspectOutsourcingLabelingAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'item']


admin.site.register(LabelImage)
admin.site.register(InspectImage)
