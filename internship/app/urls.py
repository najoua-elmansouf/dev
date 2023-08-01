from django.urls import path, include
from . import views
from app.dash_apps.finished_apps import example
app_name = 'app'
urlpatterns = [
    path('', views.myview),
    path('upload_datasets/', views.upload_datasets, name='upload_datasets'),
    # Remove the following line, as it includes 'chatbot.urls' with the same path
    # path('upload_datasets/', include('chatbot.urls')), 
    path('graph/', views.myview, name="graph"),
    # Other URL patterns for the app if needed
    # ...
]
