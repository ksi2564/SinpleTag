from django.urls import path

from labeling.views import label_detail, status_board, inspect_list, inspect_detail, LabelingList, LabelingLoadImage

app_name = 'labeling'

urlpatterns = [
    path('', LabelingList.as_view(), name='label_list'),
    path('image_num/', label_detail, name='label_detail'),
    path('inspect/', inspect_list, name='inspect_list'),
    path('inspect/image_num/', inspect_detail, name='inspect_detail'),
    path('board/', status_board, name='status_board'),

    path('load/label/data', LabelingLoadImage.as_view(), name='labeling_load_data'),
]
