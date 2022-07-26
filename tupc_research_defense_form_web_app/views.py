from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from pyparsing import empty

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
##################################################################################

#  Sign up Page
def signup(request):

    form = SignUpForm()

    course = StudentCourseMajor.objects.all()
        
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
                user_check.first_name = request.POST.get('first_name_input').title()
                user_check.middle_name = request.POST.get('middle_name_input').title()
                user_check.last_name = request.POST.get('last_name_input').title()
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

    context = {'form': form, "course" : course}
    return render(request, 'signup.html', context)
##################################################################################

# Log out
def logout_user(request):
    logout(request)
    return redirect('index')


# Student - Dashboard Page
@login_required(login_url='index')
def studentDashboard(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    context = {'user_full_name': user_full_name}

    return render(request, 'student-dashboard.html', context)
##################################################################################

# Student - Profile Page
@login_required(login_url='index')
def studentProfile(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    current_username = (request.user.username)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_email = current_user.email

    user_full_name = user_first_name + " " + user_last_name

    user_course = (request.user.course)

    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
    course_name = course_check.course
    major_name = course_check.major


    context = {'user_full_name': user_full_name,
                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
               "user_course": user_course,
                'course_name' : course_name,
                'major_name' : major_name,
               'username': current_username, 
               'user_email':user_email,
               }

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
##################################################################################

# Student - Panel Conforme Page
@login_required(login_url='index')
def studentPanelConforme(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_full_name = user_first_name + " " + user_last_name

    user_middle_initial = None
    leader_member_name = None

    user_course = current_user.course

    
    if user_middle_name == "":
        leader_member_name = user_first_name + " " + user_last_name

    else:
        user_middle_initial = user_middle_name[0]
        leader_member_name = user_first_name + " " + user_middle_initial + ". " + user_last_name

    try:
        dept_head_check = User.objects.get(is_department_head=1)
        dept_head_name = dept_head_check.first_name + " " + dept_head_check.last_name

        panel_check = User.objects.filter(is_panel=1)

        panel_members = []

        for panel in panel_check:

            if panel.middle_name == "":
                print("Panel No M.I")
                panel_members.append(panel.first_name + " " + panel.last_name)

            else:
                print("Panel have M.I")
                panel_middle_initial = panel.middle_name[0]
                panel_members.append(panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)

        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        context = {
            'user_full_name': user_full_name,

            'dept_head_name': dept_head_name,

            'panel_members' : panel_members,

            'leader_member_name' : leader_member_name,
            'course_name' : course_name,
            'major_name' : major_name,
            }
        return render(request, 'student-panel-conforme.html', context)

    except:
        print("Incomplete Form")
        context = {'user_full_name': user_full_name}
        return render(request, 'student-panel-conforme.html', context)
##################################################################################


# Admin - Dashboard Page
@login_required(login_url='index')
def adminDashboard(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    context = {'user_full_name': user_full_name}

    return render(request, 'admin-dashboard.html', context)
##################################################################################

# Admin - Department Head Check
@login_required(login_url='index')
def adminDepartmentHead(request):

    try:
        dept_head_check = User.objects.get(is_department_head=1)
        print(dept_head_check.username)
        print("Account Exist")
        return redirect('admin-department-head-acc')

    except:
        print("Create Account")
        return redirect('admin-department-head-create')
##################################################################################

# Admin - Department Head Create Account Page
@login_required(login_url='index')
def adminDepartmentHeadCreateAcc(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

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
                user_check.department = "Industrial Technology"
                user_check.is_department_head = 1
                user_check.is_student = 0
                user_check.save()

                context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
                    'user_last_name': user_last_name, 'username': current_user.username, 'response': "account created"}

                return render(request, 'admin-dept-head-account.html', context)

            else:
                print("password mismatch")
                context = {'user_full_name': user_full_name, 'user_first_name': user_first_name, 'user_last_name': user_last_name,
                    'username': current_user.username, 'form': form, 'response': 'password mismatch'}
                return render(request, 'admin-dept-head-create-acc.html', context)

        else:
            print("user exist")
            context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
                'user_last_name': user_last_name, 'username': current_user.username, 'form': form, 'response': 'user exist'}
            return render(request, 'admin-dept-head-create-acc.html', context)

    context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
        'user_last_name': user_last_name, 'username': current_user.username, 'form': form}
    return render(request, 'admin-dept-head-create-acc.html', context)
##################################################################################

# Admin - Department Head Account Page
@login_required(login_url='index')
def adminDepartmentHeadAcc(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    dept_head_check = User.objects.get(is_department_head=1)

    print(dept_head_check.username)
    dept_head_username = dept_head_check.username
    dept_head_email = dept_head_check.email
    dept_head_first_name = dept_head_check.first_name
    dept_head_last_name = dept_head_check.last_name
    dept_head_department = dept_head_check.department

    context = {
        'user_full_name': user_full_name,
        'dept_head_username': dept_head_username,
        'dept_head_email': dept_head_email,
        'dept_head_first_name': dept_head_first_name,
        'dept_head_last_name': dept_head_last_name,
        'dept_head_department': dept_head_department,
        }

    return render(request, 'admin-dept-head-account.html', context)
##################################################################################

# Admin - Student Add Course and Major Page
@login_required(login_url='index')
def adminStudentAddCourseMajor(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    if request.method == "POST":
        course_input = request.POST.get('course_input')
        major_input = request.POST.get('major_input')
        course_abbr_input = request.POST.get('course_abbr_input')

        print(course_input)

        if StudentCourseMajor.objects.filter(major=major_input).exists():
            print("Major doesn't exist")

            context = {
            'user_full_name': user_full_name, 
            'response': "major exist",
            }

            return render(request, 'admin-student-add-course-major.html', context)
            
        elif StudentCourseMajor.objects.filter(course_major_abbr=course_abbr_input).exists():
            print("Course Abbreviation doesn't exist")

            context = {
            'user_full_name': user_full_name, 
            'response': "course abbr exist",
            }

            return render(request, 'admin-student-add-course-major.html', context)
            
        else:
            print("save")
            queryForm = StudentCourseMajor(course=course_input, major=major_input, course_major_abbr=course_abbr_input)
            queryForm.save()

            context = {
            'user_full_name': user_full_name, 
            'response': "added successfully",
            }

            return render(request, 'admin-student-add-course-major.html', context)

    context = {
        'user_full_name': user_full_name, 
        }

    return render(request, 'admin-student-add-course-major.html', context)


# Admin - Faculty Member Check
@login_required(login_url='index')
def adminFacultyMember(request):

    try:
        members = User.objects.all().filter(is_panel=1)
        print("Account Exist")
        return redirect('admin-faculty-member-acc')

    except:
        print("Create Account")
        return redirect('admin-faculty-member-create')
##################################################################################

# Admin - Faculty Member Create Account Page
@login_required(login_url='index')
def adminFacultyMemberCreateAcc(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

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
                # user_check.department = "Industrial Technology"
                user_check.is_panel = 1
                user_check.is_student = 0
                # user_check.is_adviser = 1
                # user_check.is_subject_teacher = 1
                user_check.save()

                context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
                    'user_last_name': user_last_name, 'username': current_user.username, 'response': "account created"}

                return render(request, 'admin-faculty-member-account.html', context)

            else:
                print("password mismatch")
                context = {'user_full_name': user_full_name, 'user_first_name': user_first_name, 'user_last_name': user_last_name,
                    'username': current_user.username, 'form': form, 'response': 'password mismatch'}
                return render(request, 'admin-faculty-member-create-acc.html', context)

        else:
            print("user exist")
            context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
                'user_last_name': user_last_name, 'username': current_user.username, 'form': form, 'response': 'user exist'}
            return render(request, 'admin-faculty-member-create-acc.html', context)

    context = {'user_full_name': user_full_name, 'user_first_name': user_first_name,
        'user_last_name': user_last_name, 'username': current_user.username, 'form': form}
    return render(request, 'admin-faculty-member-create-acc.html', context)
##################################################################################

# Admin - Department Head Account Page
@login_required(login_url='index')
def adminFacultyMemberAcc(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_last_name = current_user.last_name

    user_full_name = user_first_name + " " + user_last_name

    members = User.objects.all().filter(is_panel=1)

    # dept_head_check = User.objects.get(is_panel=1)

    # print(dept_head_check.username)
    # dept_head_username = dept_head_check.username
    # dept_head_email = dept_head_check.email
    # dept_head_first_name = dept_head_check.first_name
    # dept_head_last_name = dept_head_check.last_name
    # dept_head_department = dept_head_check.department

    context = {
        'user_full_name': user_full_name,
        'members' : members,
        # 'dept_head_username': dept_head_username,
        # 'dept_head_email': dept_head_email,
        # 'dept_head_first_name': dept_head_first_name,
        # 'dept_head_last_name': dept_head_last_name,
        # 'dept_head_department': dept_head_department,
        }

    return render(request, 'admin-faculty-member-account.html', context)
##################################################################################