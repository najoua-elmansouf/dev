from django.urls import path,include
from . import views
from app.dash_apps.finished_apps import example, graphs
#from app.dash_apps.finished_apps import graphs
app_name = 'app'
urlpatterns = [

     # Remove the duplicate URL pattern 'upload_datasets/'
    path('upload_datasets/', views.upload_datasets, name='upload_datasets'),
    
    # Remove the following line, as it includes 'chatbot.urls' with the same path
    # path('upload_datasets/', views.upload_datasets, name='upload_datasets')
    
    # Include the URL patterns for the 'chatbot' app
    path('upload_datasets/', include('chatbot.urls')), 
    
    # Add URL pattern for the 'graph' view defined in views.py
    path('graph/', views.myview, name='graph'),
    
    # Other URL patterns for the app if needed
    # ...
]
