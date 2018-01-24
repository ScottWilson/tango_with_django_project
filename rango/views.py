from django.shortcuts import render

from django.http import HttpResponse

# Import Category model
from rango.models import Category
from rango.models import Page

def show_category(request, category_name_slug):
    # Create context dictionary to be passed to
    # template rendering engine
    context_dict = {}

    try:
        # Try and find category name slug with the given name
        # False: raises DoesNotExist exception
        # True: returns one model instance
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all associated pages (either list of page
        # objects or empty list)
        pages = Page.objects.filter(category=category)

        # Add results list to template context under name pages
        context_dict['pages'] = pages
        # Add category object from database
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Don't do anything - the following displays a 'no category'
        # message

        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)

def index(request):
    # Query database for a list of all categories currently stored
    # Order categories by number of likes in descending order (top 5 only)
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'boldmessage': "Take this out if the tests fail!!!"}

    return render(request, 'rango/about.html', context=context_dict)

