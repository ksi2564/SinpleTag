from django.contrib import admin

# Register your models here.
from classification.models import InitialImage, ClassificationImage, ClassificationInspectImage


class InitialImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image', 'label_user', 'inspect_user')
    actions = ['label_user_null', 'inspect_user_null']

    def label_user_null(self, request, queryset):
        queryset.update(label_user=None)

    def inspect_user_null(self, request, queryset):
        queryset.update(inspect_user=None)

    label_user_null.short_description = '작업자 초기화'
    inspect_user_null.short_description = '전문가 초기화'


class ClassificationImageAdmin(admin.ModelAdmin):
    list_filter = ('image_type',)
    list_display = ('__str__', 'image_type')


class ClassificationInspectImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'labeling_user', 'label_inspect_user')


admin.site.register(InitialImage, InitialImageAdmin)
admin.site.register(ClassificationImage, ClassificationImageAdmin)
admin.site.register(ClassificationInspectImage, ClassificationInspectImageAdmin)
