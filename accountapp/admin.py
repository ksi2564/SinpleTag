from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User
from django.db.models import Count

from accountapp.decorators import is_login
from accountapp.models import RequestPermission

admin.site.login = is_login(admin.site.login)  # 로그인 후 어드민페이지 접속 가능
admin.site.unregister(User)


# Users 테이블 상세 보기에 RequestPermission 테이블 추가
class RequestPermissionInline(admin.TabularInline):
    model = RequestPermission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_staff', ('requestpermission', admin.EmptyFieldListFilter))  # requestpermission 요청 유뮤를 필터로 추가
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'classification_pass', 'labeling_pass')
    actions = ['author_staff', 'unauthor_staff', 'permission_delete']
    inlines = [RequestPermissionInline]
    search_fields = ('email',)

    def permission_delete(self, request, queryset):
        for obj in queryset.all():
            RequestPermission.objects.filter(user_id=obj).delete()

    def author_staff(self, request, queryset):
        queryset.update(is_staff=True)
        self.permission_delete(request, queryset)

    def unauthor_staff(self, request, queryset):
        queryset.update(is_staff=False)

    def classification_pass(self, obj):
        return obj.classification_pass

    def labeling_pass(self, obj):
        return obj.labeling_pass

    def get_queryset(self, request):
        queryset = super(UserAdmin, self).get_queryset(request)
        queryset = queryset.annotate(
            classification_pass=Count('label_user__classificationimage__classificationinspectimage', distinct=True),
            labeling_pass=Count('labeling_user__labelimage__inspectimage', distinct=True))
        return queryset

    author_staff.short_description = '전문가 권한 부여'
    unauthor_staff.short_description = '전문가 권한 해제'
    permission_delete.short_description = '전문가 권한 요청 삭제'


@admin.register(RequestPermission)
class RequestPermissionAdmin(admin.ModelAdmin):
    pass
