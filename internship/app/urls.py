from django.urls import path 
from . import views
from app.dash_apps.finished_apps import example, graphs

urlpatterns = [
    path('graph/',views.myview,name="graph"),
    path('upload_datasets/', views.upload_datasets, name='upload_datasets'),
]