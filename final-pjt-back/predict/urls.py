from django.contrib import admin
from django.urls import path
from . import views
app_name='predict'

urlpatterns = [
    path('get-predict/<str:ticker_code>/', views.get_predict),
]
