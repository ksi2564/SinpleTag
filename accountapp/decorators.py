from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect


def is_login(func):
    def decorated(request, *args, **kwargs):
        session = request.user.pk

        if session:
            return func(request, *args, **kwargs)
        else:
            messages.error(request, '로그인을 먼저 해주세요', extra_tags='danger')
            return redirect('account_login')

    return decorated


def is_staff(func):
    def decorated(request, *args, **kwargs):
        user = User.objects.get(pk=request.user.pk)
        if user.is_staff is True:
            return func(request, *args, **kwargs)
        else:
            messages.error(request, '권한이 없습니다. 전문가 요청 승인 시 이용 가능합니다.', extra_tags='danger')
            return redirect('mainpage')

    return decorated
