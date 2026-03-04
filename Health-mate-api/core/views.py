from django.shortcuts import render
from django.conf import settings
import pyrebase
from requests import request

config = settings.FIREBASE_CONFIG

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

def signIn(request):

    return render(request, 'signIn.html')

def postsign(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = auth.sign_in_with_email_and_password(email, password)
    return render(request, 'welcome.html', {'email': email})



