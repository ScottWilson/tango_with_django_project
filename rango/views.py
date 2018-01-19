from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there partner!\nTry <a href='/rango/about/'>About</a> for the 'about' page.")

def about(request):
    return HttpResponse("Rango says here is the about page. Use <a href='/rango/'>Index</a> to return to the main page.")

