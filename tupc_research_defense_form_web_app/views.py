from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm
from .models import *

User = get_user_model()

# Index / Log in Page
def index(request):

    if request.method == 'POST':
        username_form = request.POST.get('username_input')
        password_form = request.POST.get('password_input')

        print(username_form)
        print(password_form)

        try:
            user_check = User.objects.get(username=username_form)

            if user_check.is_student == 1:
                if user_check.password == password_form:
                    user = User.objects.get(
                        username=username_form, password=password_form)
                    login(request, user)
                    return redirect('student-dashboard')

                else:
                    print("Incorrect Password")
                    context = {'response': "incorrect password"}
                    return render(request, 'index.html', context)
            
            elif user_check.is_administrator == 1:
                    if user_check.password == password_form:
                        user = User.objects.get(
                            username=username_form, password=password_form)
                        login(request, user)
                        return redirect('admin-dashboard')

                    else:
                        print("Incorrect Password")
                        context = {'response': "incorrect password"}
                        return render(request, 'index.html', context)

            else:
                print("Unauthorize Access")
                context = {'response': "unauthorized access"}
                return render(request, 'index.html', context)

        except:
            print("User does not exist")
            context = {'response': "user does not exist"}
            return render(request, 'index.html', context)

    return render(request, 'index.html')

#  Sign up Page
def signup(request):

    form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(request.POST)

        confirm_password = request.POST.get('confirm_password_input')
        print(confirm_password)

        if form.is_valid():
            print("valid form")

            user = form.save(commit=False)

            if user.password == confirm_password:
                print("valid password")
                user.save()

                user_check = User.objects.get(username=user.username)
                user_check.first_name = request.POST.get('first_name_input')
                user_check.last_name = request.POST.get('last_name_input')
                user_check.course = request.POST.get('course_input')
                user_check.is_student = 1
                user_check.save()

                login(request, user)
                return redirect('student-dashboard')

            else:
                print("invalid password")
                context = {'form': form, 'response': "password mismatch"}
                return render(request, 'signup.html', context)

        else:
            print("user exist")
            context = {'form': form, 'response': "user exist"}
            return render(request, 'signup.html', context)

        print("user exist")
        context = {'form': form, 'response': "user exist"}
        return render(request, 'signup.html', context)

    context = {'form': form}
    return render(request, 'signup.html', context)

# Log out
def logout_user(request):
    logout(request)
    return redirect('index')


@login_required(login_url='index')
# Student - Dashboard Page
def studentDashboard(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    context = {'user_full_name': user_full_name}

    return render(request, 'student-dashboard.html', context)


@login_required(login_url='index')
# Student - Panel Conforme Page
def studentProfile(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    current_username = (request.user.username)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    user_course = (request.user.course)

    context = {'user_full_name': user_full_name,
               'username': current_username, "user_course": user_course}

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get(
            'confirm_new_password_input')

        if current_password_input == currentpassword:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(
                        password=new_password_input)

                    context = {'user_full_name': user_full_name, 'username': current_username,
                               "user_course": user_course, "response": "success"}
                    return render(request, 'student-profile.html', context)

                else:
                    context = {'user_full_name': user_full_name, 'username': current_username,
                               "user_course": user_course, "response": "new password and confirm new password doesnt match"}
                    return render(request, 'student-profile.html', context)

            else:
                context = {'user_full_name': user_full_name, 'username': current_username,
                           "user_course": user_course, "response": "current password and new password is same"}
                return render(request, 'student-profile.html', context)

        else:
            context = {'user_full_name': user_full_name, 'username': current_username,
                       "user_course": user_course, "response": "current password is incorrect"}
            return render(request, 'student-profile.html', context)

    return render(request, 'student-profile.html', context)


# Student - Panel Conforme Page
@login_required(login_url='index')
def studentPanelConforme(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    context = {'user_full_name': user_full_name}

    return render(request, 'student-panel-conforme.html', context)


@login_required(login_url='index')
# Admin - Dashboard Page
def adminDashboard(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    context = {'user_full_name': user_full_name}

    return render(request, 'admin-dashboard.html', context)