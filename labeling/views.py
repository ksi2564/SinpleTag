from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView

from labeling.models import RequestPermission


def main_page(request):
    return render(request, 'main_page2.html')


def login(request):
    return render(request, 'login.html')


# def my_info(request):
#     return render(request, 'my_info.html')


class MyInfo(DetailView):
    model = User
    template_name = 'my_info.html'

    def dispatch(self, request, *args, **kwargs):
        user_pk = request.user.pk
        url_pk = self.kwargs['pk']

        if user_pk is url_pk:
            return super(MyInfo, self).dispatch(request)
        messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
        return redirect(reverse("labeling:mainpage"))

    def post(self, request, *args, **kwargs):
        new_request = RequestPermission()
        new_request.user = self.request.user
        new_request.name = self.request.user.socialaccount_set.all()[0].extra_data['name']
        new_request.save()

        messages.success(request, "전문가 권한 요청을 하였습니다.")
        return redirect(self.request.path_info)


def classification_list(request):
    return render(request, 'classification_list.html')


def classification_detail(request):
    return render(request, 'classification_detail.html')


# def permission(request):
#     return render(request, 'permission.html')


def label_list(request):
    return render(request, 'label_list.html')


def label_detail(request):
    return render(request, 'label_detail.html')


def inspect_list(request):
    return render(request, 'inspect_list.html')


def inspect_detail(request):
    return render(request, 'inspect_detail.html')


# def data_upload(request):
#     return render(request, 'data_upload.html')


def status_board(request):
    return render(request, 'status_board.html')
