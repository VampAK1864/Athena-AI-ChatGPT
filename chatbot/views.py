import uuid

from django.shortcuts import render, redirect  # Add the redirect import.
from django.http import JsonResponse  # Add the JsonResponse import.
import openai  # Import the openai module.

from django.contrib import auth  # Add the auth import.
from django.contrib.auth.models import User  # Add the User import.
from .models import Chat  # Import the Chat model.

from django.utils import timezone  # Add the timezone import.
from django.shortcuts import render
from .models import Chat, ChatRoom

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Chat, ChatRoom

from django.urls import path
from . import views

openai_api_key = 'YOUR_API_KEY'  # Replace YOUR_API_KEY with your openai apikey
openai.api_key = openai_api_key  # Set the api key to the openai api key


# def clear_recent_actions(request): # Define the clear_recent_actions view.
#     LogEntry.objects.all().delete() # Delete all the LogEntry objects.
#     return HttpResponse("Recent actions cleared.") # Return a HttpResponse object with the message "Recent actions cleared.".


def ask_openai(message, conversation_history):  # Define the ask_openai function.
    conversation_history.append({"role": "user",
                                 "content": message})  # Append a new dictionary to the conversation_history list with the role "user" and the content of the message.
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    answer = response.choices[
        0].message.content.strip()  # Set the answer variable to the content of the first message in the response.choices list.
    conversation_history.append({"role": "assistant",
                                 "content": answer})  # Append a new dictionary to the conversation_history list with the role "assistant" and the content of the answer.
    return answer, conversation_history  # Return the answer and the conversation_history list.


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('create_chatroom')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                chat_room = ChatRoom.objects.filter(users__in=[user]).first()
                if chat_room is None:
                    chat_room = ChatRoom.objects.create()
                    chat_room.users.add(user)
                return redirect('chatbot', chat_id=chat_room.id if chat_room else None)
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def logout(request):  # Define the logout view.
    auth.logout(request)  # Log out the user.
    return redirect('login')  # Redirect to the login page.


from django.utils import timezone


@login_required
@login_required
def view_chat(request, chat_id):
    try:
        chat_room = ChatRoom.objects.get(id=chat_id)  # Try to get the chatroom
        request.session['current_chatroom'] = chat_room.id
        print(f"Current chatroom ID: {request.session['current_chatroom']}")  # Print the current chatroom ID
    except ChatRoom.DoesNotExist:
        return redirect('create_chatroom')  # If chatroom does not exist, redirect to create_chatroom

    if request.method == 'POST':
        if chat_id:  # Check if a chat_id is provided
            new_chat_name = request.POST.get('chat_name')  # Get the new chat name from the POST request
            chat_room.chat_name = new_chat_name  # Update the chat name
            chat_room.save()
            request.session['current_chatroom'] = chat_room.id
            chat_rooms = ChatRoom.objects.filter(users=request.user)
        else:
            return redirect('create_chatroom')
    return redirect('chatbot', chat_id=chat_room.id)


@login_required
def chatbot(request, chat_id):
    chat_rooms = ChatRoom.objects.filter(users=request.user)  # Fetch chat rooms for the current user
    if request.method == 'POST':
        chat_room = ChatRoom.objects.get(id=chat_id)
        message = request.POST.get('message')
        conversation_history = []
        chats = Chat.objects.filter(chat_room=chat_room).order_by('created_at')
        for chat in chats:
            conversation_history.append(
                {"role": "user" if chat.user == request.user else "assistant", "content": chat.message})
            conversation_history.append({"role": "assistant", "content": chat.response})

        response, conversation_history = ask_openai(message, conversation_history)

        chat = Chat.objects.create(
            chat_room=chat_room,
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now()
        )

        return JsonResponse({'response': response})
    current_chatroom_id = chat_id
    chat_room = ChatRoom.objects.get(id=chat_id)
    chats = Chat.objects.filter(chat_room=chat_room).order_by('created_at')
    return render(request, 'chatbot.html',
                  {'chats': chats, 'chat_rooms': chat_rooms, 'current_chatroom_id': current_chatroom_id})


@login_required
def create_chatroom(request):
    if request.method == 'POST':
        chat_room = ChatRoom.objects.create(chat_name=f"Chat with {request.user.username}")
        chat_room.users.add(request.user)
    else:
        chat_room = ChatRoom.objects.create(chat_name=f"Chat with {request.user.username}")
        chat_room.users.add(request.user)
    return redirect('view_chat', chat_id=chat_room.id)


@login_required
def delete_chatroom(request, chat_id):
    if request.method == 'POST':
        current_chatroom_id = request.session.get('current_chatroom')
        chat_room = ChatRoom.objects.get(id=chat_id)
        if request.user in chat_room.users.all():
            chat_room.delete()
            # Get the ID of the currently displayed chatroom from the session
            if current_chatroom_id:
                # If the deleted chatroom was the one being displayed, redirect to create_chatroom
                if (current_chatroom_id) == chat_id:
                    return redirect('create_chatroom')
                # Otherwise, redirect to the currently displayed chatroom
                else:
                    return redirect('view_chat', chat_id=current_chatroom_id)
            else:
                return redirect('create_chatroom')
