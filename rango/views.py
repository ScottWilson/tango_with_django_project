from django.shortcuts import render
from django.http import HttpResponse
from rango.forms import CategoryForm, PageForm

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

def add_category(request):
    form = CategoryForm()

    # HTTP post
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Check for valid form
        if form.is_valid():
            form.save(commit=True) # Save new category to database
            return index(request)
        else:
            print(form.errors)

    # Render the form (with error messages if any)
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)

def index(request):
    # Query database for a list of all categories currently stored
    # Order categories by number of likes in descending order (top 5 only)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories': category_list, 'pages': page_list}

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'boldmessage': "Take this out if the tests fail!!!"}

    return render(request, 'rango/about.html', context=context_dict)

