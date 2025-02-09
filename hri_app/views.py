from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import HttpResponse
import csv
from .models import Feedback

def home(request):
    return render(request, 'hri_app/home.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:  # Check if user is a superuser
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'hri_app/admin_login.html', {'error': 'Invalid credentials or not an admin.'})
    return render(request, 'hri_app/admin_login.html')

def experimentee_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'hri_app/experimentee_login.html', {'error': 'Invalid credentials.'})
    return render(request, 'hri_app/experimentee_login.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'hri_app/signup.html', {'error': 'Username already taken. Please choose another.'})

        try:
            # Create the user only if the username is unique
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect('home')
        except IntegrityError:
            return render(request, 'hri_app/signup.html', {'error': 'An error occurred. Please try again.'})

    return render(request, 'hri_app/signup.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def animation(request, animation_type):
    context = {
        'animation_type': animation_type,
        'num_leds': 10,  # Number of LEDs in the strip
    }
    return render(request, 'hri_app/animation.html', context)

def feedback(request, animation_type):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        rating = request.POST.get('rating')
        Feedback.objects.create(user_name=user_name, animation_type=animation_type, rating=rating)
        return redirect('thank_you')  # Redirect to Thank You page
    return render(request, 'hri_app/feedback.html', {'animation_type': animation_type})

def thank_you_view(request):
    return render(request, 'hri_app/thank_you.html')

def download_feedback(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedback.csv"'
    writer = csv.writer(response)
    writer.writerow(['User Name', 'Animation Type', 'Rating', 'Timestamp'])
    for entry in Feedback.objects.all():
        writer.writerow([entry.user_name, entry.animation_type, entry.rating, entry.comments, entry.timestamp])
    return response