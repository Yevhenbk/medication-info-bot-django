from django.urls import path
from . import views

urlpatterns = [
    # path('get_chat/', views.get_chat, name='get_chat'),
    path('create_message/<int:chat_id>/', views.create_message, name='create_message'),
    path('get_messages/<int:chat_id>/', views.get_messages, name='get_messages'),
    path('get_chats/', views.get_chats, name='get_chats'),
    path('create_chat/', views.create_chat, name='create_chat')
]