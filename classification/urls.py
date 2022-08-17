from django.urls import path

from classification.views import ClassificationList, ClassificationDetail, ClassificationInspectList, \
    ClassificationLoadImage, ClassificationInspectLoadImage, pass_or_not, \
    classification_dataset, image_api, ClassificationStatusBoard

app_name = 'classification'

urlpatterns = [
    path('imageapi/', image_api, name='image_api'),

    path('', ClassificationList.as_view(), name='classification_list'),
    path('<int:pk>/', ClassificationDetail.as_view(), name='classification_detail'),
    path('inspect/', ClassificationInspectList.as_view(), name='classification_inspect_list'),
    path('board/', ClassificationStatusBoard.as_view(), name='classification_status_board'),

    path('load/classify/data', ClassificationLoadImage.as_view(), name='classification_load_data'),
    path('load/inspect/data', ClassificationInspectLoadImage.as_view(), name='classification_inspect_load_data'),
    path('pass/', pass_or_not, name='pass_or_not'),
    path('dataset/', classification_dataset, name='classification_dataset'),
]
