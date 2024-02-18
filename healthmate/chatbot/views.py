from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message
from transformers import pipeline
import requests
import re


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


def get_medication_info(user_question):
    try:
        # Extract medication name and selected_info from the user's question
        match = re.match(r"^(?P<medication_name>[\w\s]+),\s*(?P<selected_info>[\w\s]+)$", user_question.strip())
        if match:
            medication_name = match.group("medication_name")
            selected_info = match.group("selected_info").lower()

            if not selected_info:
                # If selected_info is not specified, default to the entire formatted_info
                selected_info = 'full_info'

            # Replace spaces with underscores in selected_info
            selected_info_key = selected_info.replace(' ', '_').lower()

            endpoint = f'https://api.fda.gov/drug/label.json?api_key=t62Chde4gVkYohphhcmfh6VKb0aH4i2nBaSasURK&search=openfda.generic_name:{medication_name}&limit=1'

            response = requests.get(endpoint)
            response.raise_for_status()

            data = response.json()

            if 'results' in data and data['results']:
                medication_data = data['results'][0]
                formatted_info = format_medication_info(medication_data, selected_info_key)
                return formatted_info
            else:
                return f"No information found for {medication_name}."

        else:
            return "Invalid input format. Please provide both medication name and selected information separated by a comma (e.g., Aspirin, Warnings)."

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def format_medication_info(data, selected_info=None):
    # Format the medication information for a user-friendly response
    try:
        formatted_info = f"Information about {data['openfda']['generic_name'][0]}:\n"

        if not selected_info:
            # If no specific info is selected, include all available information
            formatted_info += f"Active Ingredient: {', '.join(data['active_ingredient'])}\n"
            formatted_info += f"Purpose: {', '.join(data['purpose'])}\n"
            formatted_info += f"Indications and Usage: {', '.join(data['indications_and_usage'])}\n"
            formatted_info += f"\nWarnings: {', '.join(data['warnings'])}\n"
            formatted_info += f"Do Not Use: {', '.join(data['do_not_use'])}\n"
            formatted_info += f"Ask Doctor: {', '.join(data['ask_doctor'])}\n"
            formatted_info += f"Ask Doctor or Pharmacist: {', '.join(data['ask_doctor_or_pharmacist'])}\n"
            formatted_info += f"Stop Use: {', '.join(data['stop_use'])}\n"
            formatted_info += f"Pregnancy and Breastfeeding: {', '.join(data['pregnancy_or_breast_feeding'])}\n"
            formatted_info += f"Keep Out of Reach of Children: {', '.join(data['keep_out_of_reach_of_children'])}\n"
            formatted_info += f"Dosage and Administration: {', '.join(data['dosage_and_administration'])}\n"
            formatted_info += f"Storage and Handling: {', '.join(data['storage_and_handling'])}\n"
        else:
            # Include only the selected information
            selected_info = selected_info.lower()
            if selected_info in data:
                formatted_info += f"{', '.join(data[selected_info])}\n"
            else:
                formatted_info += f"Selected information '{selected_info}' not found.\n"

        return formatted_info
    except KeyError:
        return "Error formatting medication information."


@login_required
def create_message(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        user_question = request.POST.get('question', '')

        # Use the Medication Information chatbot
        response = get_medication_info(user_question)

        message = Message.objects.create(chat=chat, sender=request.user, question=user_question, response=response)

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