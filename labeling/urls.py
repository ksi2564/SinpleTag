from django.urls import path

from labeling.views import label_list, label_detail, status_board, inspect_list, inspect_detail

app_name = 'labeling'

urlpatterns = [
    path('', label_list, name='label_list'),
    path('image_num/', label_detail, name='label_detail'),
    path('inspect/', inspect_list, name='inspect_list'),
    path('inspect/image_num/', inspect_detail, name='inspect_detail'),
    path('board/', status_board, name='status_board'),
]
