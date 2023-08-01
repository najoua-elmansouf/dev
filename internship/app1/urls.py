from django.urls import path
from . import views

urlpatterns = [
    path('signup',views.SignupPage, name='signup'),
    path('login/',views.LoginPage, name='login'),
    path('fassil/',views.FassilPage, name='fassil'),
    path('HomePage/',views.HomePage, name='HomePage'),
    path('logout/',views.LogoutPage, name='logout'),
    path('',views.AccueilPage, name='accueil'),
]