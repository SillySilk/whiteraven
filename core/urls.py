from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('location/', views.location, name='location'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('api/status/', views.current_status_api, name='current_status_api'),
    path('site-images/', views.site_images_manager, name='site_images'),
    path('bulk-upload/', views.bulk_image_upload, name='bulk_upload'),
]