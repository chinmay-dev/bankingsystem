from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('manager/<str:pk>', views.manager, name="manager"),
    path('customer/<str:pk>/', views.customer, name="customer"),
    path('transact/<str:pk>/', views.transact, name="transact"),
]
