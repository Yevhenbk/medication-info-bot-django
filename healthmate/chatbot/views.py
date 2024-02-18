from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message
import torch
from transformers import pipeline

question_answerer = pipeline("question-answering", model='deepset/roberta-base-squad2')


@login_required
def chat_view(request):
    if request.method == 'POST':
        user_question = request.POST.get('question')
        ai_response = request.POST.get('response')  # Assuming response is generated on the frontend
        user = request.user
        chat, created = Chat.objects.get_or_create(user=user)
        
        # Save the user's question and AI's response to the database
        message = Message.objects.create(chat=chat, user_question=user_question, ai_response=ai_response)
        
        # Return JSON response indicating success
        return JsonResponse({'success': True})
    else:
        # Render the chat interface
        return render(request, 'chat.html')
    

@login_required
def create_message(request, chat_id):
    try:
        # Ensure the requesting user has access to the specified chat
        chat = Chat.objects.get(id=chat_id, user=request.user)

        # Get the question from the POST data
        user_question = request.POST.get('question', '')

        # Define the context (you may retrieve it from your dataset or other sources)
        context = "Anna is 19 years old and lives in Paris."

        # Generate response using the question answering pipeline
        response = question_answerer(question=user_question, context=context)["answer"]

        # Create a new message
        message = Message.objects.create(chat=chat, sender=request.user, question=user_question, response=response)

        # Return the generated response
        return JsonResponse({'success': True, 'message_id': message.id, 'response': response})
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        messages = Message.objects.filter(chat=chat)
        message_list = [{'sender': msg.sender.username, 'question': msg.question, 'response': msg.response} for msg in messages]
        return JsonResponse({'messages': message_list})
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)


@login_required
def get_chats(request):
    user_chats = Chat.objects.filter(user=request.user)
    chat_list = [{'id': chat.id, 'title': chat.title} for chat in user_chats]
    return JsonResponse({'chats': chat_list})


@login_required
def create_chat(request):
    try:
        # Assuming you have a 'title' field in your POST data
        title = request.POST.get('title', 'New Chat')  # Default to 'New Chat' if not provided

        new_chat = Chat.objects.create(user=request.user, title=title)
        return JsonResponse({'success': True, 'chat_id': new_chat.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})