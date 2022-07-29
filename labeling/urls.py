from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from labeling.views import main_page, login, label_list, label_detail, status_board, inspect_list, inspect_detail, \
    MyInfo

app_name = 'labeling'

urlpatterns = [
    path('', main_page, name='mainpage'),
    path('login/', login, name='login'),
    path('myinfo/<int:pk>/', MyInfo.as_view(), name='my_info'),
    path('label/', label_list, name='label_list'),
    path('label/image_num/', label_detail, name='label_detail'),
    path('inspect/', inspect_list, name='inspect_list'),
    path('inspect/image_num/', inspect_detail, name='inspect_detail'),
    path('board/', status_board, name='status_board'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
