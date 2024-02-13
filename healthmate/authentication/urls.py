from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.sign_up, name='sign_up'),
    path('login/', views.log_in, name='log_in'),
    path('logout/', views.log_out, name='logout'),
    path('restricted/', views.restricted_view, name='restricted')
]