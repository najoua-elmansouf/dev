from django.urls import path
from . import views

app_name = 'chatbot_app'

urlpatterns = [
    path('', views.chat_view, name='chat_view'), 
    # Other URL patterns for the chatbot app if needed
    # ...
]
