from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render


# Create your views here.


def main_page(request):
    social_account = SocialAccount.objects.last()
    return render(request, 'main_page2.html', context={'social_account': social_account})


def login(request):
    return render(request, 'login.html')


def my_info(request):
    return render(request, 'my_info.html')


def label_list(request):
    return render(request, 'label_list.html')


def label_detail(request):
    return render(request, 'label_detail.html')


def inspect_list(request):
    return render(request, 'inspect_list.html')


def inspect_detail(request):
    return render(request, 'inspect_detail.html')


def data_upload(request):
    return render(request, 'data_upload.html')


def status_board(request):
    return render(request, 'status_board.html')
