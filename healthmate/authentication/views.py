from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# from django.http import HttpResponseForbidden
# from .models import Chat, Message


def home(request):
    return render(request, 'home.html')


def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home') 
    else:
        form = UserCreationForm()
    return render(request, 'sign_up.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'log_in.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('home')


@login_required
def restricted_view(request):
    return render(request, 'restricted.html')