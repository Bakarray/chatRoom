from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Message
from django.conf import settings

# Create your views here.
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    page = 'login'
    context = {'page': page}

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'groupChat/auth.html', context)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'groupChat/auth.html', context)


def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    page = 'signup'

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email').lower()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                login(request, user)
                return redirect('home')
    
    context = {'page': page}
    return render(request, 'groupChat/auth.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')


def home(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            image = request.FILES.get('image')

            if content or image:
                Message.objects.create(
                    sender=request.user, 
                    content=content,
                    image=image
                    )
                return redirect('home')
        else:
            messages.error(request, 'You need to login to send messages')
            return redirect('login')
    
    chat_messages = Message.objects.all().order_by('created_at')
    context = {
        'chat_messages': chat_messages,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'groupChat/home.html', context)