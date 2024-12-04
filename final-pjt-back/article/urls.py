from django.urls import path
from . import views
app_name='article'
urlpatterns = [
    path('list/', views.article_list),
    path('<int:article_pk>/',views.article_detail ),
    path('create/',views.article_create ),
    path('<int:article_pk>/modify/',views.article_modify ),
    path('<int:article_pk>/delete/', views.article_delete),
    path('<int:article_pk>/comments/create/', views.comment_create),
    path('<int:article_pk>/comments/<int:comment_pk>/update/', views.comment_update),
    path('<int:article_pk>/comments/<int:comment_pk>/delete/', views.comment_delete),
]