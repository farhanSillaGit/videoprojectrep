from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('', views.video_list, name='video_list'),
    path('videos/',views.video_list, name='video_list'),
]
