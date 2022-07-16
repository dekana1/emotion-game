from django.urls import path

from . import views

app_name = 'game'

urlpatterns = [
    path('', views.front, name='front'),
    path('home', views.home, name='home'),
    path('result', views.predictor, name='predictor'),
    
    
]

