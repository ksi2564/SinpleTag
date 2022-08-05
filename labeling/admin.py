from django.contrib import admin

# Register your models here.
from labeling.models import LabelImage


admin.site.register(LabelImage)
