from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView

from accountapp.models import RequestPermission


def login(request):
    return render(request, 'login.html')


class MyInfo(DetailView):
    model = User
    template_name = 'my_info.html'

    def dispatch(self, request, *args, **kwargs):
        user_pk = request.user.pk
        url_pk = self.kwargs['pk']

        if user_pk is not url_pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("mainpage"))
        return super(MyInfo, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def post(self, request, *args, **kwargs):
        new_request = RequestPermission()
        new_request.user = self.request.user
        new_request.name = self.request.user.socialaccount_set.all()[0].extra_data['name']
        new_request.save()

        messages.success(request, "전문가 권한 요청을 하였습니다.")
        return redirect(self.request.path_info)  # url 주소에 따라 참조되어야하는 view를 결정 즉, self 참조
