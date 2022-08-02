from django.contrib import admin

# Register your models here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from labeling.models import RequestPermission, InitialImage, ClassificationImage

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

    def author_staff(self, request, queryset):
        queryset.update(is_staff=True)

    def unauthor_staff(self, request, queryset):
        queryset.update(is_staff=False)

    def permission_delete(self, request, queryset):
        for obj in queryset.all():
            RequestPermission.objects.filter(user_id=obj).delete()

    author_staff.short_description = '전문가 권한 부여'
    unauthor_staff.short_description = '전문가 권한 해제'
    permission_delete.short_description = '전문가 권한 요청 삭제'


class InitialImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image', 'label_user', 'inspect_user')
    actions = ['label_user_null', 'inspect_user_null']

    def label_user_null(self, request, queryset):
        queryset.update(label_user=None)

    def inspect_user_null(self, request, queryset):
        queryset.update(inspect_user=None)

    label_user_null.short_description = '작업자 초기화'
    inspect_user_null.short_description = '전문가 초기화'


admin.site.register(User, UserAdmin)
admin.site.register(RequestPermission)
admin.site.register(InitialImage, InitialImageAdmin)
admin.site.register(ClassificationImage)
