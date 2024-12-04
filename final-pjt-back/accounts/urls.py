from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
app_name='account'

urlpatterns = [
     path('check-username/', views.check_username, name='check_username'),
     path('find-id/', views.find_id, name='find_id'),
     path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
     path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
     path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name="password_reset_confirm"),
     path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
     path('profile/', views.profile, name='profile'),
     path('edit/', views.edit_user_profile, name='edit'),
     path('add-product/', views.add_product_to_account, name='add_product'),
     path('remove-product/', views.remove_product_from_account, name='remove_product'),
     path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]