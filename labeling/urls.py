from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from labeling.views import main_page, login, label_list, label_detail, status_board, inspect_list, inspect_detail, \
    MyInfo, ClassificationList, ClassificationDetail, delete_object_function, ClassificationLoadImage, \
    ClassificationInspectList, ClassificationInspectLoadImage, just_test

app_name = 'labeling'

urlpatterns = [
    path('', main_page, name='mainpage'),
    path('login/', login, name='login'),
    path('myinfo/<int:pk>/', MyInfo.as_view(), name='my_info'),
    path('classification/', ClassificationList.as_view(), name='classification_list'),
    path('classification/<int:pk>/', ClassificationDetail.as_view(), name='classification_detail'),
    path('classification/inspect/', ClassificationInspectList.as_view(), name='classification_inspect_list'),
    path('label/', label_list, name='label_list'),
    path('label/image_num/', label_detail, name='label_detail'),
    path('inspect/', inspect_list, name='inspect_list'),
    path('inspect/image_num/', inspect_detail, name='inspect_detail'),
    path('board/', status_board, name='status_board'),

    path('load/classify/data', ClassificationLoadImage.as_view(), name='classification_load_data'),
    path('load/inspect/data', ClassificationInspectLoadImage.as_view(), name='classification_inspect_load_data'),
    path('delete/<int:pk>', delete_object_function, name='classification_delete'),
    path('just/test', just_test, name='just_test'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
