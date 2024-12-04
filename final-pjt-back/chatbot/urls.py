from django.urls import path
from . import views
app_name='chatbot'
urlpatterns = [
    path('chat/', views.chat ),
    path('make-portfolio/', views.make_portfolio ),
    path('investment-styles/', views.investment_style_type_view, name='investment-style-type'),
    path('save-user-investment-style/', views.save_user_investment_style, name='save_user_investment_style'),
    path('get-user-investment-style/', views.get_user_investment_style, name='get_user_investment_style'),
    path('portfolio/<int:portfolio_id>/', views.get_portfolio, name='get-portfolio'),
    path('latest-portfolio/', views.get_latest_portfolio, name='latest-portfolio'),
]