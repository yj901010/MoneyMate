from django.contrib import admin
from django.urls import path, include
from . import views
app_name='finlife'

urlpatterns = [
    path('save-deposit-products/', views.save_deposit_product),
    path('deposit-products/', views.deposit_product),
    path('deposit-products-options/<str:fin_prdt_cd>/', views.deposit_product_options),
    path('deposit-products/top_rate/', views.top_rate),
    path('change/', views.save_change),
    path('getchange/<str:cur_unit>/', views.get_change),
    path('getBankName/', views.get_bankname),
    path('<str:fin_prdt_cd>/top_rate_month/', views.top_rate_month),
    path('news/', views.get_news),
    path('getchanges/', views.get_changes, name='get_changes'),
]
