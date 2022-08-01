from django.contrib import admin

# Register your models here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from labeling.models import RequestPermission, InitialImage

admin.site.login = login_required(admin.site.login)
admin.site.unregister(User)


# Users 테이블 상세 보기에 RequestPermission 테이블 추가
class RequestPermissionInline(admin.TabularInline):
    model = RequestPermission


class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_staff', ('requestpermission', admin.EmptyFieldListFilter))  # requestpermission 요청 유뮤를 필터로 추가
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'requestpermission')
    actions = ['author_staff', 'unauthor_staff', 'permission_delete']
    inlines = [RequestPermissionInline]
    search_fields = ('email',)

    # 전문가 권한 부여
    def author_staff(self, request, queryset):
        queryset.update(is_staff=True)

    # 전문가 권한 해제
    def unauthor_staff(self, request, queryset):
        queryset.update(is_staff=False)

    def permission_delete(self, request, queryset):
        for obj in queryset.all():
            RequestPermission.objects.filter(user_id=obj).delete()

    author_staff.short_description = '전문가 권한 부여'
    unauthor_staff.short_description = '전문가 권한 해제'
    permission_delete.short_description = '요청 거절'


admin.site.register(User, UserAdmin)
admin.site.register(RequestPermission)
admin.site.register(InitialImage)
