from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-in/', views.sign_in, name='sign-in'),
    path('logout/', views.logout, name='logout'),
    
    path('settings/', views.settings, name='settings'),
    path('profile/<str:pk>', views.profile, name='profile'),
    
    path('upload', views.uploads, name='upload'),
    path('like-post/', views.like_post, name='like-post'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
]
