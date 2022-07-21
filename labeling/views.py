from django.shortcuts import render

# Create your views here.


def main_page(request):
    return render(request, 'main_page2.html')


def login(request):
    return render(request, 'login.html')


def label_list(request):
    return render(request, 'label_list.html')


def my_info(request):
    return render(request, 'my_info.html')


def data_upload(request):
    return render(request, 'data_upload.html')


def label_detail(request):
    return render(request, 'label_detail.html')


def status_board(request):
    return render(request, 'status_board.html')
