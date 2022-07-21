from django.urls import path

from labeling.views import main_page, login, label_list, my_info, data_upload, label_detail, status_board

app_name = 'labeling'

urlpatterns = [
    path('', main_page, name='mainpage'),
    path('login/', login, name='login'),
    path('label/', label_list, name='label_list'),
    path('myinfo/', my_info, name='my_info'),
    path('data/', data_upload, name='data_upload'),
    path('label/image_num/', label_detail, name='label_detail'),
    path('board/', status_board, name='status_board'),
]
