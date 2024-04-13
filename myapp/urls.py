from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_aadhar, name='upload_aadhar'),
    path('result/', views.view_result, name='view_result'),
]
