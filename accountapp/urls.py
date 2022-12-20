from django.urls import path

from accountapp.views import login, my_info, permission_req

app_name = 'accountapp'

urlpatterns = [
    path('login/', login, name='login'),
    path('<int:pk>/', my_info, name='my_info'),
    path('permission/', permission_req, name='permission_req'),
]
