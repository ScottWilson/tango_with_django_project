from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there partner!\nTry 'rango/about' for the 'about' page.")

def about(request):
    return HttpResponse("Rango says here is the about page. Use 'rango/' to return to the main page.")

