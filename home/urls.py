from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login', views.LoginInterfaceView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register', views.RegisterInterfaceView.as_view(), name='register'),
]