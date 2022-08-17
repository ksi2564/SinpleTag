from django.urls import path

from labeling.views import LabelingList, LabelingLoadImage, LabelingDetail, \
    LabelingInspectList, LabelingInspectLoadImage, LabelingInspectDetail, delete_object_function, LabelingStatusBoard

app_name = 'labeling'

urlpatterns = [
    path('', LabelingList.as_view(), name='label_list'),
    path('<int:pk>/', LabelingDetail.as_view(), name='label_detail'),
    path('inspect/', LabelingInspectList.as_view(), name='inspect_list'),
    path('inspect/<int:pk>/', LabelingInspectDetail.as_view(), name='inspect_detail'),
    path('board/', LabelingStatusBoard.as_view(), name='labeling_status_board'),

    path('load/label/data', LabelingLoadImage.as_view(), name='labeling_load_data'),
    path('load/inspect/data', LabelingInspectLoadImage.as_view(), name='labeling_inspect_load_data'),
    path('delete/<int:pk>', delete_object_function, name='labeling_object_delete'),
]
