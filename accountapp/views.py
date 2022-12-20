from allauth.account.views import SignupView
from django.contrib import messages, admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView

from accountapp.models import RequestPermission


def login(request):
    return render(request, 'login.html')


class MyInfo(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'my_info.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.pk != self.kwargs['pk']:
            return redirect(reverse("accountapp:my_info", kwargs={"pk": request.user.pk}))
        return super().dispatch(request, *args, **kwargs)


my_info = MyInfo.as_view()


@login_required
def permission_req(request):
    request_user = RequestPermission(user=request.user)
    social_account = request.user.socialaccount_set.all()[0].extra_data['name']
    request_user.name = social_account if social_account else request.user.username
    request_user.save()
    messages.success(request, "전문가 권한을 요청했습니다.")
    return redirect(reverse("accountapp:my_info", kwargs={"pk": request.user.pk}))
