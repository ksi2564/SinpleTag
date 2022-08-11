from django.contrib import admin

# Register your models here.
from category.models import TopCategory, Item, HeelHeight, Sole, Material, Detail, Color, Printing

admin.site.register(TopCategory)
admin.site.register(Item)
admin.site.register(HeelHeight)
admin.site.register(Sole)
admin.site.register(Material)
admin.site.register(Printing)
admin.site.register(Detail)
admin.site.register(Color)
