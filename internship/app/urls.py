from django.urls import path 
from . import views
from app.dash_apps.finished_apps import example, graphs

urlpatterns = [
    path('',views.myview),
    path('upload_datasets/', views.upload_datasets, name='upload_datasets'),
]