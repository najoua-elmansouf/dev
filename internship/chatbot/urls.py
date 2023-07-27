from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'), 
    path('pdf_recieve/', views.pdf_recieve, name='pdf_recieve'),
      # Correct name 'chat_view'
    # Other URL patterns for your app if needed
    # ...
]