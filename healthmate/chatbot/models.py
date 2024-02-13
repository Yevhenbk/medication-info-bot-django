from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class TodoItem(models.Model):
    title=models.CharField(max_length=100)
    completed=models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class Chat(models.Model):
    title = models.CharField(max_length=100, blank=True)  # Title generated only on the first interaction
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()

    def __str__(self):
        return f"{self.sender.username} in {self.chat.title}"