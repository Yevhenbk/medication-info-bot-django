from django.contrib import admin
from .models import TodoItem, Chat, Message

admin.site.register(TodoItem)
admin.site.register(Chat)
admin.site.register(Message)
