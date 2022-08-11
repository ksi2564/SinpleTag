from django.contrib import messages
from django.shortcuts import redirect


def is_login(func):
    def decorated(request, *args, **kwargs):
        session = request.user.pk

        if session:
            return func(request, *args, **kwargs)
        else:
            messages.error(request, '로그인을 먼저 해주세요', extra_tags='danger')
            return redirect('accountapp:login')

    return decorated
