from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-image/', views.generate_image, name='generate_image'),
    path('generate-video/', views.generate_video, name='generate_video'),
]