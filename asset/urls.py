from django.urls import path
from . import views

app_name = 'asset'

urlpatterns = [
    path('index/', views.index, name="index"),
    path('list/ajax/', views.list_ajax, name="list_ajax"),
    path('delete/ajax/', views.delete_ajax, name="delete_ajax"),
    path('get/ajax/', views.get_ajax, name="get_ajax"),
    path('edit/ajax/', views.edit_ajax, name='edit_ajax'),
    path('get_resource/ajax/', views.get_resource_ajax, name='get_resource_ajax'),
]