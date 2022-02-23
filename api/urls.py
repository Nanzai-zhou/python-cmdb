from django.urls import path
from .views import v1

app_name = 'api'

urlpatterns = [
    path('v1/client/<str:ip>/', v1.ClientView.as_view(), name='client'),
    path('v1/client/<str:ip>/resource/', v1.ResourceView.as_view(), name='resource'),
    path('v1/client/<str:ip>/heartbeat/', v1.HeartBeatView.as_view(), name='heartbeat'),
]