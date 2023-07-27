from django.urls import path,include
from . import views
from app.dash_apps.finished_apps import example

urlpatterns = [
    path('',views.myview),
    path('upload_datasets/', views.upload_datasets, name='upload_datasets'),
    path('upload_datasets/', include('chatbot.urls')), 
]