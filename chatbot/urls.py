from django.urls import path
from . import views

urlpatterns = [
    path('create_chatroom/', views.create_chatroom, name='create_chatroom'),
    path('view_chat/<int:chat_id>/', views.view_chat, name='view_chat'),
    path('chatbot/<int:chat_id>/', views.chatbot, name='chatbot'),
    path('delete_chatroom/<int:chat_id>/', views.delete_chatroom, name='delete_chatroom'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]