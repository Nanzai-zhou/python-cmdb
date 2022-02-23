from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('index/', views.index, name="index"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('delete/', views.delete, name='delete'),
    path('edit/', views.edit, name='edit'),
    path('change/', views.change, name='change'),
    path('signup/', views.signup, name='signup'),
    path('create/', views.create, name='create'),
    path('create/ajax/', views.create_ajax, name='create_ajax'),
    path('delete/ajax/', views.delete_ajax, name='delete_ajax'),
    path('edit/ajax/', views.edit_ajax, name='edit_ajax'),
]