from django.urls import path

from accountapp.views import login, MyInfo

app_name = 'accountapp'

urlpatterns = [
    path('login/', login, name='login'),
    path('myinfo/<int:pk>/', MyInfo.as_view(), name='my_info'),
]
