from django.contrib import admin

# Register your models here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

admin.site.login = login_required(admin.site.login)
admin.site.unregister(User)


class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_staff',)
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    actions = ['author_staff', 'unauthor_staff']

    def author_staff(self, request, queryset):
        queryset.update(is_staff=True)

    def unauthor_staff(self, request, queryset):
        queryset.update(is_staff=False)

    author_staff.short_description = '전문가 권한 부여'
    unauthor_staff.short_description = '전문가 권한 해제'


admin.site.register(User, UserAdmin)
