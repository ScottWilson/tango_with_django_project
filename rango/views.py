from django.shortcuts import render
from django.http import HttpResponse
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from datetime import datetime

# Import Category model
from rango.models import Category
from rango.models import Page

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get number of visits to the site
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit:
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # Set last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # update visits cookie
    request.session['visits'] = visits
                    

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
    request.session.set_test_cookie()
    
    # Query database for a list of all categories currently stored
    # Order categories by number of likes in descending order (top 5 only)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return response

def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKING!")
        request.session.delete_test_cookie()

    visitor_cookie_handler(request)

    context_dict = {'boldmessage': "Take this out if the tests fail!!!"}
    context_dict['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dict)

def register(request):
    # Registration success flag
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save user form data to database
            user = user_form.save()

            # Hash password with set_password() then save
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # If user provided a profile picture:
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            # Update flag to show template registration was successful
            registered = True
        else:
            # Invalid form or forms, print to terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not an HTTP POST
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})

def user_login(request):
    # if request is an HTTP POST, try and pull relevant information
    if request.method == 'POST':
        # Get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # return user object with authenticated info
        user = authenticate(username=username, password=password)

        # presence of user object: details correct
        # if None: no user with details correct
        if user:
            # check if account disabled
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        # Not an HTTP POST, likely HTTP GET so display login form
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    context_dict = {'boldmessage': "This page is restricted! Try logging out."}
    
    return render(request, 'rango/restricted.html', context=context_dict)
            
@login_required
def user_logout(request):
    # We know the user is logged in so we can just log out
    logout(request)
    return HttpResponseRedirect(reverse('index'))



