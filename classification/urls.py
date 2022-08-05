from django.urls import path

from classification.views import ClassificationList, ClassificationDetail, ClassificationInspectList, \
    ClassificationLoadImage, ClassificationInspectLoadImage, delete_object_function, just_test

app_name = 'classification'

urlpatterns = [
    path('', ClassificationList.as_view(), name='classification_list'),
    path('<int:pk>/', ClassificationDetail.as_view(), name='classification_detail'),
    path('inspect/', ClassificationInspectList.as_view(), name='classification_inspect_list'),

    path('load/classify/data', ClassificationLoadImage.as_view(), name='classification_load_data'),
    path('load/inspect/data', ClassificationInspectLoadImage.as_view(), name='classification_inspect_load_data'),
    path('delete/<int:pk>', delete_object_function, name='classification_delete'),
    path('just/test', just_test, name='just_test'),
]
