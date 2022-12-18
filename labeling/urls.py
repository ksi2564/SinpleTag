from django.urls import path

from labeling.views import LabelingList, LabelingLoadImage, LabelingDetail, \
    LabelingInspectList, LabelingInspectLoadImage, LabelingInspectDetail, delete_object_function, LabelingStatusBoard, \
    excel_export, LabelingOutsourcingList, LabelingOutsourcingDetail, \
    outsourcing_json_deserializer1, outsourcing_json_deserializer2

app_name = 'labeling'

urlpatterns = [
    path('', LabelingList.as_view(), name='label_list'),
    path('<int:pk>/', LabelingDetail.as_view(), name='label_detail'),
    path('inspect/', LabelingInspectList.as_view(), name='inspect_list'),
    path('inspect/<int:pk>/', LabelingInspectDetail.as_view(), name='inspect_detail'),
    path('board/', LabelingStatusBoard.as_view(), name='labeling_status_board'),
    path('outsourcing/', LabelingOutsourcingList.as_view(), name='outsourcing_list'),
    path('outsourcing/<int:pk>/', LabelingOutsourcingDetail.as_view(), name='outsourcing_detail'),

    path('load/label/data', LabelingLoadImage.as_view(), name='labeling_load_data'),
    path('load/inspect/data', LabelingInspectLoadImage.as_view(), name='labeling_inspect_load_data'),
    path('delete/<int:pk>', delete_object_function, name='labeling_object_delete'),

    path('export/', excel_export, name='export_excel'),

    path('osc/', outsourcing_json_deserializer1, name='outsourcing_json_deserializer1'),
    path('osc/mtm', outsourcing_json_deserializer2, name='outsourcing_json_deserializer2'),
]
