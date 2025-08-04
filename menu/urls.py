from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('filter/', views.menu_filter_ajax, name='menu_filter_ajax'),
    path('<slug:slug>/', views.menu_item_detail, name='menu_item_detail'),
]