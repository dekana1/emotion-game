from django.urls import path

from . import views

app_name = 'game'

urlpatterns = [
    path('', views.front, name='front'),
    path('signup', views.signup, name='signup'),
    path('user_login', views.user_login, name='user_login'),
    path('check_username', views.check_username, name='check_username'),
    path('home', views.home, name='home'),
    path('result', views.predictor, name='predictor'),
    path('logout/', views.logout, name='logout'),
    
    
]

