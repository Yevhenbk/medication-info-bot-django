from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message


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