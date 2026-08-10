from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query/', views.query, name='query'),
    path('reviews/', views.reviews, name='reviews'),
    path('feedback/', views.feedback, name='feedback'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/forgot/', views.api_forgot, name='api_forgot'),
]
