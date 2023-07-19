from django.urls import path 
from . import views
from app.dash_apps.finished_apps import example

urlpatterns = [
    path('',views.myview),
]