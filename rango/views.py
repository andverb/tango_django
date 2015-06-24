from django.shortcuts import render
from rango.models import Category, Page, UserProfile
from django.contrib.auth.models import User
from rango.forms import CategoryForm, PageForm
from rango.forms import UserProfileForm
from django.views.generic import ListView

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
        else:
            # Cookie last_visit doesn't exist, so create it to the current date/time.
            reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response


def about(request):

    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # remember to include the visit data
    return render(request, 'rango/about.html', {'visits': count})
    # return HttpResponse("About page <br/> <a href='/rango'>Home</a>")

def category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print (form.errors)
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat, 'category_name_slug' : category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


@login_required
def restricted(request):

    return render(request,'rango/restricted.html',{"restricted_text" :"Since you're logged in, you can see this text!"})

def track_url(request, page_id):
    if request.method == 'GET':
        if page_id:
            requested_page = Page.objects.get(id=page_id)
            if requested_page:
                requested_page.views += 1
                print(requested_page, requested_page.views)
                requested_page.save()
            return redirect(requested_page.url)
        else:
            return redirect('/rango/')
# TODO make slugs fo profiles, add links to list of users and to current user profile to navbar
def profile(request, user_id):
    saved = False
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        if profile_form.is_valid():
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            if 'picture' in request.FILES:
                user_profile.picture = request.FILES['picture']
            user_profile.save()
            saved = True
        else:
            print(profile_form.errors)
    else:
        profile_form = UserProfileForm(instance=user_profile)

    context_dic = {'saved': saved, 'user': user, 'user_profile': user_profile, 'profile_form': profile_form}
    return render(request, 'rango/profile.html', context_dic)


class UsersList(ListView):
    model = User
    template_name = 'rango/users_list.html'
    context_object_name = 'users_list'
