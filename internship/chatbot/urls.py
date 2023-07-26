from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),  # Correct name 'chat_view'
    # Other URL patterns for your app if needed
    # ...
]