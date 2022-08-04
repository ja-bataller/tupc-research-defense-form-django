import email
from multiprocessing import context
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from pyparsing import empty

from .forms import SignUpForm
from .models import *

from datetime import date

from docx import Document
from docx2pdf import convert
import os
from docx.shared import Inches

today = date.today()

# User = get_user_model()

##########################################################################################################################

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

    course = StudentCourseMajor.objects.all()

    course_list = []

    if not course:
        context = {
            'response': "sweet no course"}
        return render(request, 'signup.html', context)
    
    else:
        for course_abbr in course:
            course_list.append(course_abbr.course_major_abbr)
        
        print(course_list)

    if request.method == "POST":
        form = SignUpForm(request.POST)

        course_input = request.POST.get('course_input')
        confirm_password = request.POST.get('confirm_password_input')

        print(confirm_password)

        if course_input == "default":

            context = {
                'form': form, 
                "course" : course,

                'response': "choose course"
            }

            return render(request, 'signup.html', context)

        if course_input not in course_list:

            context = {
                'form': form, 
                "course" : course,

                'response': "sweet invalid course"
            }

            return render(request, 'signup.html', context)

        if form.is_valid():
            print("valid form")

            user = form.save(commit=False)

            user_username_inut = user.username
            user_email_inut = user.email

            if "TUPC" in user_username_inut:
                pass

            else:
                context = {'form': form,"course" : course, 'response': "invalid username"}
                return render(request, 'signup.html', context)
            
            if "gsfe.tupcavite.edu.ph" in user_email_inut:
                pass

            else:
                context = {'form': form,"course" : course, 'response': "invalid email"}
                return render(request, 'signup.html', context)

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
                context = {'form': form,"course" : course, 'response': "password mismatch"}
                return render(request, 'signup.html', context)

        else:
            print("user exist")
            context = {'form': form, "course" : course, 'response': "user exist"}
            return render(request, 'signup.html', context)

        print("user exist")
        context = {'form': form, 'response': "user exist"}
        return render(request, 'signup.html', context)

    context = {
        'form': form, 
        "course" : course
        }
    
    return render(request, 'signup.html', context)

# Log out
def logout_user(request):
    logout(request)
    return redirect('index')

##########################################################################################################################

# Student - Dashboard Page
@login_required(login_url='index')
def studentDashboard(request):
    current_user = (request.user)

    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"
    

    # PANEL CONFORME BET-3
    try:
        panel_conforme_bet3_check = PanelConformeBET3.objects.get(student_leader_username=current_user)

        research_title = panel_conforme_bet3_check.research_title

        department_head = panel_conforme_bet3_check.dept_head
        department_head_status = panel_conforme_bet3_check.dept_head_status

        panel_member_1 = panel_conforme_bet3_check.panel_member_1
        panel_member_2 = panel_conforme_bet3_check.panel_member_2
        panel_member_3 = panel_conforme_bet3_check.panel_member_3
        panel_member_4 = panel_conforme_bet3_check.panel_member_4
        panel_member_5 = panel_conforme_bet3_check.panel_member_5

        panel_member_status_1 = panel_conforme_bet3_check.panel_member_status_1
        panel_member_status_2 = panel_conforme_bet3_check.panel_member_status_2
        panel_member_status_3 = panel_conforme_bet3_check.panel_member_status_3
        panel_member_status_4 = panel_conforme_bet3_check.panel_member_status_4
        panel_member_status_5 = panel_conforme_bet3_check.panel_member_status_5

        context = {
        'user_full_name': user_full_name,
        'user_account': user_account,

        'research_title' : research_title,

        'form': "Panel Conforme (BET-3)",

        'department_head': department_head,
        'department_head_status' : department_head_status,

        'panel_member_1':panel_member_1,
        'panel_member_2':panel_member_2,
        'panel_member_3':panel_member_3,
        'panel_member_4':panel_member_4,
        'panel_member_5':panel_member_5,

        'panel_member_status_1':panel_member_status_1,
        'panel_member_status_2':panel_member_status_2,
        'panel_member_status_3':panel_member_status_3,
        'panel_member_status_4':panel_member_status_4,
        'panel_member_status_5':panel_member_status_5,
        }

        return render(request, 'student-dashboard.html', context)
    
    except:
        pass
    
    context = {
        'user_full_name': user_full_name,
        'user_account': user_account
        }

    return render(request, 'student-dashboard.html', context)


# Student - Profile Page
@login_required(login_url='index')
def studentProfile(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    # Topbar
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    # Student Profile
    current_username = (request.user.username)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_email = current_user.email

    user_course = (request.user.course)

    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
    course_name = course_check.course
    major_name = course_check.major


    context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'user_course': user_course,  
                'course_name' : course_name,
                'major_name' : major_name,
                'username': current_username, 
                'user_email':user_email,
                }   

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == currentpassword:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'user_first_name': user_first_name,
                        'user_middle_name' : user_middle_name,
                        'user_last_name' : user_last_name,
                        'user_course': user_course,  
                        'course_name' : course_name,
                        'major_name' : major_name,
                        'username': current_username, 
                        'user_email':user_email,

                        "response": "new password and confirm new password doesnt match"
                        }

                    return render(request, 'student-profile.html', context)

            else:
                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'user_first_name': user_first_name,
                    'user_middle_name' : user_middle_name,
                    'user_last_name' : user_last_name,
                    'user_course': user_course,  
                    'course_name' : course_name,
                    'major_name' : major_name,
                    'username': current_username, 
                    'user_email':user_email,

                    "response": "current password and new password is same"
                    }

                return render(request, 'student-profile.html', context)

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'user_course': user_course,  
                'course_name' : course_name,
                'major_name' : major_name,
                'username': current_username, 
                'user_email':user_email, 

                "response": "current password is incorrect"
                }

            return render(request, 'student-profile.html', context)

    return render(request, 'student-profile.html', context)


# Student - Panel Conforme BET-3 Process
@login_required(login_url='index')
def studentPanelConformeBet3(request):
    current_user = (request.user)

    try:
        PanelConformeBET3.objects.get(student_leader_username=current_user)
        print("Panel Conforme - BET-3 Exist")
        return redirect('student-panel-conforme-bet3-form')

    except:
        panel_members = User.objects.all().filter(is_panel=1)
        
        try:
            dept_head_check = User.objects.get(is_department_head=1)
            pass
        except:
            print("No DIT Head")
            context = {
                'response' : "sweet inc form"
            }

            return render(request, 'student-panel-conforme-bet-3-create.html', context)

        if not panel_members or panel_members.count() < 5:
            print("Incomplete Faculty Member")
            context = {
                'response' : "sweet inc form"
            }

            return render(request, 'student-panel-conforme-bet-3-create.html', context)
        else:
            pass


        print("Panel Conforme - BET-3 Create")
        return redirect('student-panel-conforme-bet3-create')


# Student - Panel Conforme BET-3 Create Page
@login_required(login_url='index')
def studentPanelConformeBet3Create(request):
    current_user = (request.user)

    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    # Topbar End

    leader_member_name = None
    leader_member_name_2 = None

    user_course = current_user.course
    
    if user_middle_name == "":
        leader_member_name = current_user.first_name + " " + current_user.last_name
        leader_member_name_2 = current_user.last_name + ", " + current_user.first_name

    else:
        user_middle_initial = user_middle_name[0]
        leader_member_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name
        leader_member_name_2 = current_user.last_name + ", " + current_user.first_name + " " + user_middle_initial + "."


    panel_member_check_list = []
    panel_members = User.objects.all().filter(is_panel=1)

    for panel_member in panel_members:

        if panel_member.middle_name == "":
            panel_member_check_list.append(panel_member.honorific + " " + panel_member.first_name + " " + panel_member.last_name)
        else:
            panel_member_check_list.append(panel_member.honorific + " " + panel_member.first_name + " " + panel_member.middle_name[0] + ". " + panel_member.last_name)

    print(panel_member_check_list)

    if request.method == "POST":

        # Get Text Month, Day Year - Today
        date_today = today.strftime("%B %d, %Y")
        print("Date Submitted =", date_today)

        # Get Research Title Input
        research_title_input = request.POST.get('research_title_input')
        print("Research Title =", research_title_input)

        # Get Full Course Name and Full Major Name
        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        # Shorten the word "Engineering" to "Eng." - for the Generating of PDF Form
        course_input = course_name
        course_abbr = course_input.replace("Engineering", "Eng.")
        print("Course =", course_abbr)

        major_input = major_name
        print("Major =", major_input)

        # Get Department of Industrial Technology Head Name
        dept_head_check = User.objects.get(is_department_head=1)
        dept_head_name_input = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name
        print("Department Head =", dept_head_name_input)

        # Get Panel Member 1 Name
        panel1_input = request.POST.get('panel1_input')
        print("Panel 1 =", panel1_input)

        # Get Panel Member 2 Name
        panel2_input = request.POST.get('panel2_input')
        print("Panel 2 =", panel2_input)

        # Get Panel Member 3 Name
        panel3_input = request.POST.get('panel3_input')
        print("Panel 3 =", panel3_input)

        # Get Panel Member 4 Name
        panel4_input = request.POST.get('panel4_input')
        print("Panel 4 =", panel4_input)

        # Get Panel Member 5 Name
        panel5_input = request.POST.get('panel5_input')
        print("Panel 5 =", panel5_input)

        # Get Student Leader or Member 1 Name
        student1_input = leader_member_name_2
        print("Student 1 =", student1_input)

        # Get Student Member 2 Name
        student2_input = request.POST.get('student2_input')
        print("Student 2 =", student2_input)

         # Get Student Member 3 Name
        student3_input = request.POST.get('student3_input')
        print("Student 3 =", student3_input)

         # Get Student Member 4 Name
        student4_input = request.POST.get('student4_input')
        print("Student 4 =", student4_input)

         # Get Student Member 5 Name
        student5_input = request.POST.get('student5_input')
        print("Student 5 =", student5_input)

        # If the Student already has a Panel Conform BET-3
        try:
            PanelConformeBET3.objects.get(student_leader_username=current_user.username)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                panel_members_list = []

                for panel in panel_check:

                    if panel.middle_name == "":
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

                    else:
                        panel_middle_initial = panel.middle_name[0]
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
                
                panel_members = sorted(panel_members_list)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'dept_head_name': dept_head_name,

                    'panel_members' : panel_members,

                    'leader_member_name' : leader_member_name_2,
                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "panel conforme bet-3 exist"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')
                    
        except:
            pass

        #  If Research Title is existing
        try:
            ResearchTitle.objects.get(research_title=research_title_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                panel_members_list = []

                for panel in panel_check:

                    if panel.middle_name == "":
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

                    else:
                        panel_middle_initial = panel.middle_name[0]
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
                
                panel_members = sorted(panel_members_list)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'dept_head_name': dept_head_name,

                    'panel_members' : panel_members,

                    'leader_member_name' : leader_member_name_2,
                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "existing research title"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')
                    
        except:
            pass
        
        # If Panel Input is Default
        if panel1_input == "default" or panel2_input == "default" or panel3_input == "default" or panel4_input == "default" or panel5_input == "default":
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                panel_members_list = []

                for panel in panel_check:

                    if panel.middle_name == "":
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

                    else:
                        panel_middle_initial = panel.middle_name[0]
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
                
                panel_members = sorted(panel_members_list)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'dept_head_name': dept_head_name,

                    'panel_members' : panel_members,

                    'leader_member_name' : leader_member_name_2,
                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "choose 5 panel"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # If Panel Name input is the same with the other Panel Name Input
        elif panel1_input == panel2_input or panel1_input == panel3_input or panel1_input == panel4_input or panel1_input == panel5_input or panel2_input == panel1_input or panel2_input == panel3_input or panel2_input == panel4_input or panel2_input == panel5_input or panel3_input == panel1_input or panel3_input == panel2_input or panel3_input == panel4_input or panel3_input == panel5_input or panel4_input == panel1_input or panel4_input == panel2_input or panel4_input == panel3_input or panel4_input == panel5_input or panel5_input == panel1_input or panel5_input == panel2_input or panel5_input == panel3_input or panel5_input == panel4_input: 
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                panel_members_list = []

                for panel in panel_check:

                    if panel.middle_name == "":
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

                    else:
                        panel_middle_initial = panel.middle_name[0]
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
                
                panel_members = sorted(panel_members_list)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'dept_head_name': dept_head_name,

                    'panel_members' : panel_members,

                    'leader_member_name' : leader_member_name_2,
                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "same panel"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # If Panel Name input is not in the Panel Member List
        elif panel1_input not in panel_member_check_list or panel2_input not in panel_member_check_list or panel3_input not in panel_member_check_list or panel4_input not in panel_member_check_list or panel5_input not in panel_member_check_list: 
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                panel_members_list = []

                for panel in panel_check:

                    if panel.middle_name == "":
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

                    else:
                        panel_middle_initial = panel.middle_name[0]
                        panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
                
                panel_members = sorted(panel_members_list)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'dept_head_name': dept_head_name,

                    'panel_members' : panel_members,

                    'leader_member_name' : leader_member_name_2,
                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "sweet panel not in the list"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # Saving Data to MYSQL Database
        panel_conforme_form = PanelConformeBET3(
            student_leader_username = current_user,
            dept_head = dept_head_name_input, 
            dept_head_status = 'pending',

            panel_member_1 = panel1_input,
            panel_member_2 = panel2_input,
            panel_member_3 = panel3_input,
            panel_member_4 = panel4_input,
            panel_member_5 = panel5_input,

            panel_member_status_1 = "waiting for DIT Head",
            panel_member_status_2 = "waiting for DIT Head",
            panel_member_status_3 = "waiting for DIT Head",
            panel_member_status_4 = "waiting for DIT Head",
            panel_member_status_5 = "waiting for DIT Head",

            student_member_1 = student1_input,
            student_member_2 = student2_input,
            student_member_3 = student3_input,
            student_member_4 = student4_input,
            student_member_5 = student5_input,

            course = course_abbr,
            major = major_input,

            research_title = research_title_input.title(),

            date_submitted = date_today,

            form_status = "Pending"
            )

        panel_conforme_form.save()

        research_title_form = ResearchTitle(
            research_title =  research_title_input.title(),
            course = course_name,
            major = major_input,
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            status = "ongoing",
            )

        research_title_form.save()

        return redirect('student-dashboard')


    try:
        dept_head_check = User.objects.get(is_department_head=1)
        dept_head_name = None

        panel_check = User.objects.filter(is_panel=1)
 
        panel_members_list = []

        if dept_head_check.middle_name == "":
            dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name
        
        else:
            dept_head_middle_initial = dept_head_check.middle_name[0]
            dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_middle_initial + ". " + dept_head_check.last_name

        for panel in panel_check:

            if panel.middle_name == "":
                panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel.last_name)

            else:
                panel_middle_initial = panel.middle_name[0]
                panel_members_list.append(panel.honorific + " " + panel.first_name + " " + panel_middle_initial + ". " + panel.last_name)
        
        panel_members = sorted(panel_members_list)

        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        context = {
            'user_full_name': user_full_name,
            'user_account' : user_account,

            'dept_head_name': dept_head_name,

            'panel_members' : panel_members,

            'leader_member_name' : leader_member_name_2,
            'course_name' : course_name,
            'major_name' : major_name,
            }
        return render(request, 'student-panel-conforme-bet-3-create.html', context)

    except:
        print("Incomplete Form")
        context = {'user_full_name': user_full_name}
        return render(request, 'student-panel-conforme-bet-3-create.html', context)


# Student - Panel Conforme BET-3 Form Page
@login_required(login_url='index')
def studentPanelConformeBet3Form(request):
    current_user = (request.user)
    # Topbar
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    try:
        # Panel Conforme - BET-3 - Data
        panel_conforme_bet3_check = PanelConformeBET3.objects.get(student_leader_username=current_user)

        dept_head_name = panel_conforme_bet3_check.dept_head

        panel1 = panel_conforme_bet3_check.panel_member_1
        panel2 = panel_conforme_bet3_check.panel_member_2
        panel3 = panel_conforme_bet3_check.panel_member_3
        panel4 = panel_conforme_bet3_check.panel_member_4
        panel5 = panel_conforme_bet3_check.panel_member_5

        student1 = panel_conforme_bet3_check.student_member_1
        student2 = panel_conforme_bet3_check.student_member_2
        student3 = panel_conforme_bet3_check.student_member_3
        student4 = panel_conforme_bet3_check.student_member_4
        student5 = panel_conforme_bet3_check.student_member_5

        course = panel_conforme_bet3_check.course
        major = panel_conforme_bet3_check.major

        research_title = panel_conforme_bet3_check.research_title

        date_submitted = panel_conforme_bet3_check.date_submitted

        form_status = panel_conforme_bet3_check.form_status
    except:
        return redirect('student-dashboard')

    # Generate PDF Form
    if request.method == "POST":
        print("Download PDF")
        doc = Document('static/forms/2-PANEL-CONFORME.docx')

        header_table = doc.tables[0]
        student_table = doc.tables[1]
        adviser_table = doc.tables[3]
        qr_code_table = doc.tables[2]

        # print(adviser_table.cell(0, 0).text) # Adviser Name

        student1 = student_table.cell(1, 0).paragraphs[0].runs[0].text = student1
        student2 = student_table.cell(2, 0).paragraphs[0].runs[0].text = student2
        student3 = student_table.cell(3, 0).paragraphs[0].runs[0].text = student3
        student4 = student_table.cell(4, 0).paragraphs[0].runs[0].text = student4
        student5 = student_table.cell(5, 0).paragraphs[0].runs[0].text = student5

        course1 = student_table.cell(1, 2).paragraphs[0].runs[0].text = course
        course2 = student_table.cell(2, 2).paragraphs[0].runs[0].text = course
        course3 = student_table.cell(3, 2).paragraphs[0].runs[0].text = course
        course4 = student_table.cell(4, 2).paragraphs[0].runs[0].text = course
        course5 = student_table.cell(5, 2).paragraphs[0].runs[0].text = course

        major1 = student_table.cell(1, 4).paragraphs[0].runs[0].text = major
        major2 = student_table.cell(2, 4).paragraphs[0].runs[0].text = major
        major3 = student_table.cell(3, 4).paragraphs[0].runs[0].text = major
        major4 = student_table.cell(4, 4).paragraphs[0].runs[0].text = major
        major5 = student_table.cell(5, 4).paragraphs[0].runs[0].text = major

        panel_member = adviser_table.cell(0, 0).paragraphs[0].runs[0].text = dept_head_name
        date_signed = adviser_table.cell(0, 2).paragraphs[0].runs[0].text = date_submitted

        print(doc.paragraphs[1].runs[1].text) # Date Today 1
        print(doc.paragraphs[3].runs[0].text) # Receiver 1
        print(doc.paragraphs[6].runs[1].text) # Receiver 2
        print(doc.paragraphs[7].runs[1].text) # Subject
        print(doc.paragraphs[7].runs[4].text) # Student Course
        print(doc.paragraphs[7].runs[6].text) # Student Major
        print(doc.paragraphs[10].runs[1].text) # Research Title
        print(doc.paragraphs[15].runs[0].text) # Department Head Name

        doc.paragraphs[1].runs[1].text = date_submitted
        doc.paragraphs[3].runs[0].text = 'Mr. Jay Victor Gumboc'
        doc.paragraphs[6].runs[1].text = 'Mr. Jay Victor Gumboc'
        doc.paragraphs[7].runs[1].text = 'BET-3'
        doc.paragraphs[7].runs[4].text = 'Bachelor of Engineering Technology'
        doc.paragraphs[7].runs[6].text = 'Major in Computer Engienering Technology'
        doc.paragraphs[10].runs[1].text = research_title
        doc.paragraphs[15].runs[0].text = dept_head_name

        # INSERT IMAGE
        # qr_code = qr_code_table.cell(0, 0).add_paragraph()
        # qr_code_run = qr_code.add_run()
        # qr_code_run.add_picture('qr-code.png',width=Inches(0.8), height=Inches(0.8))
        # qr_code_run.alignment=WD_ALIGN_PARAGRAPH.CENTER

        
        # doc.save('2-PANEL-CONFROME-BET-3-{}.docx'.format(current_user))
        # convert('2-PANEL-CONFROME-BET-3-{}.docx'.format(current_user))
        # os.startfile('2-PANEL-CONFROME-BET-3-{}.pdf'.format(current_user))

        doc.save('2-PANEL-CONFORME-NEW.docx')
        convert("2-PANEL-CONFORME-NEW.docx")
        os.startfile('2-PANEL-CONFORME-NEW.pdf')

        context = {
        'user_full_name': user_full_name,

        'dept_head_name' : dept_head_name,

        'panel1' : panel1,
        'panel2' : panel2,
        'panel3' : panel3,
        'panel4' : panel4,
        'panel5' : panel5,

        'student1' : student1,
        'student2' : student2,
        'student3' : student3,
        'student4' : student4,
        'student5' : student5,

        'course' : course,
        'major' : major,

        'research_title' : research_title,

        'form_status' : form_status
        }
        return render(request, 'student-panel-conforme-bet-3-form.html', context)


    context = {
        'user_full_name': user_full_name,
        'user_account' : user_account,

        'dept_head_name' : dept_head_name,

        'panel1' : panel1,
        'panel2' : panel2,
        'panel3' : panel3,
        'panel4' : panel4,
        'panel5' : panel5,

        'student1' : student1,
        'student2' : student2,
        'student3' : student3,
        'student4' : student4,
        'student5' : student5,

        'course' : course,
        'major' : major,

        'research_title' : research_title,

        'form_status' : form_status
        }

    return render(request, 'student-panel-conforme-bet-3-form.html', context)

##########################################################################################################################

# Admin - Dashboard Page
@login_required(login_url='index')
def adminDashboard(request):
    current_user = (request.user)

    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    context = {
        'user_full_name': user_full_name,
        'user_account': user_account
        }

    return render(request, 'admin-dashboard.html', context)


# Admin - Profile Page
@login_required(login_url='index')
def adminProfile(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    # Topbar
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    # Admin Profile
    current_username = (request.user.username)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_email = current_user.email


    context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,
                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'username': current_username, 
                'user_email':user_email,
                }   

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == currentpassword:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'user_first_name': user_first_name,
                        'user_middle_name' : user_middle_name,
                        'user_last_name' : user_last_name,

                        'username': current_username, 
                        'user_email':user_email,

                        "response": "new password and confirm new password doesnt match"
                        }

                    return render(request, 'admin-profile.html', context)

            else:
                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'user_first_name': user_first_name,
                    'user_middle_name' : user_middle_name,
                    'user_last_name' : user_last_name,
                    'username': current_username, 
                    'user_email':user_email,

                    "response": "current password and new password is same"
                    }

                return render(request, 'admin-profile.html', context)

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'username': current_username, 
                'user_email':user_email, 

                "response": "current password is incorrect"
                }

            return render(request, 'admin-profile.html', context)

    return render(request, 'admin-profile.html', context)


# Admin - Student Add Course and Major Page
@login_required(login_url='index')
def adminStudentAddCourseMajor(request):
    current_user = (request.user)
    
    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"
    # Topbar end

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
            'user_account' : user_account,

            'response': "course abbr exist",
            }

            return render(request, 'admin-student-add-course-major.html', context)
            
        else:
            print("save")
            queryForm = StudentCourseMajor(course=course_input.title(), major=major_input.title(), course_major_abbr=course_abbr_input.upper())
            queryForm.save()

            context = {
            'user_full_name': user_full_name,
            'user_account' : user_account,
             
            'response': "added successfully",
            }

            return render(request, 'admin-student-add-course-major.html', context)

    context = {
        'user_full_name': user_full_name, 
        'user_account' : user_account,
        }

    return render(request, 'admin-student-add-course-major.html', context)


# Admin - Department Head Account Page
@login_required(login_url='index')
def adminFacultyMemberAcc(request):
    current_user = (request.user)

    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"
    # Topbar end

    members = User.objects.all().filter(is_faculty_member=1)

    # dept_head_check = User.objects.get(is_panel=1,)

    # print(dept_head_check.username)
    # dept_head_username = dept_head_check.username
    # dept_head_email = dept_head_check.email
    # dept_head_first_name = dept_head_check.first_name
    # dept_head_last_name = dept_head_check.last_name
    # dept_head_department = dept_head_check.department

    context = {
        'user_full_name': user_full_name,
        'user_account': user_account,
        'members' : members,
        # 'dept_head_username': dept_head_username,
        # 'dept_head_email': dept_head_email,
        # 'dept_head_first_name': dept_head_first_name,
        # 'dept_head_last_name': dept_head_last_name,
        # 'dept_head_department': dept_head_department,
        }

    return render(request, 'admin-faculty-member-account.html', context)

# Admin - Faculty Member Create Account Page
@login_required(login_url='index')
def adminFacultyMemberCreateAcc(request):
    current_user = (request.user)
    form = SignUpForm()

    dit_head_exist = None

    try:
        User.objects.get(is_department_head=1)
        dit_head_exist = "exist"
    except:
        pass
    
    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None
    

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Panel"
    
    elif current_user.is_adviser == 1:
        user_account = "Adviser"
    
    elif current_user.is_subject_teacher == 1:
        user_account = "Subject Teacher"
    
    elif current_user.is_academic_affairs == 1:
        user_account = "Academic Affairs"
    
    elif current_user.is_library == 1:
        user_account = "Library"
    
    elif current_user.is_research_extension == 1:
        user_account = "Research & Extension"

    elif current_user.is_administrator == 1:
        user_account = "Administrator"
    # Topbar end

    if request.method == "POST": 
        honorific_list = ["Mr.", "Ms.", "Mrs.", "Engr.", "Dr.", "Dra."]
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", 'Library', 'Research & Extension']
        
        honorific_input = request.POST.get('honorific_input')
        first_name_input = request.POST.get('first_name_input')
        middle_name_input = request.POST.get('middle_name_input')
        last_name_input = request.POST.get('last_name_input')
        user_account_input = request.POST.get('user_account_input')
        form = SignUpForm(request.POST)
        confirm_password = request.POST.get('confirm_password_input')

        print("Create Account Form")
        print("Honorofic Input: ",honorific_input)
        print("First Name: ",first_name_input)
        print("Midle Name: ",middle_name_input)
        print("Last Name: ",last_name_input)
        print("User Account: ",user_account_input)
        print("Confirm Password: ",confirm_password)


        # Form Validation Start

        if honorific_input == "Default":
            print("Choose Honorific")
            print(dit_head_exist)

            context = {
                # Topbar Start
                'user_full_name': user_full_name, 
                'user_account' : user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "choose honorific",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

        if honorific_input not in honorific_list:
            print("Honorific not in list")
            print(dit_head_exist)

            context = {
                # Topbar Start
                'user_full_name': user_full_name, 
                'user_account' : user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "honorific not in list",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

        if user_account_input == "Default":
            print("Choose User Account")
            print(dit_head_exist)

            context = {
                # Topbar Start
                'user_full_name': user_full_name, 
                'user_account' : user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "choose user account",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

        if user_account_input not in user_account_list:
            print("User Account not in list")
            print(dit_head_exist)

            context = {
                # Topbar Start
                'user_full_name': user_full_name, 
                'user_account' : user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "user account not in list",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

        if user_account_input == "DIT Head":
            try:
                User.objects.get(is_department_head=1)
                print("DIT Head Account Exist")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    'user_full_name': user_full_name, 
                    'user_account' : user_account,

                    # Form
                    'form': form,
                    'dit_head_exist' : dit_head_exist,
                }
                return render(request, 'admin-faculty-member-create-acc.html', context)

            except:
                pass

        if form.is_valid():
            user = form.save(commit=False)
            username_input = user.username
            email_input = user.email
            
            if "TUPC" not in username_input:
                print("Invalid Username")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    'user_full_name': user_full_name, 
                    'user_account' : user_account,

                    # Form
                    'form': form,
                    'dit_head_exist' : dit_head_exist,

                    # Response
                    'response' : "invalid username",
                }

                return render(request, 'admin-faculty-member-create-acc.html', context)

            if "@gsfe.tupcavite.edu.ph" not in email_input:
                print("Invalid Email")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    'user_full_name': user_full_name, 
                    'user_account' : user_account,

                    # Form
                    'form': form,
                    'dit_head_exist' : dit_head_exist,

                    # Response
                    'response' : "invalid email",
                }

                return render(request, 'admin-faculty-member-create-acc.html', context)

            if user.password == confirm_password:
                print("valid password")
                user.save()

                if user_account_input == "DIT Head":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.department = "DIT Head"
                    user_check.is_department_head = 1
                    user_check.is_panel = 1
                    user_check.is_adviser = 1
                    user_check.is_subject_teacher = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        'user_full_name': user_full_name, 
                        'user_account' : user_account,

                        'members': members,
                        # Response
                        'response' : "account created",
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Faculty Member":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.department = "Faculty Member"
                    user_check.is_panel = 1
                    user_check.is_adviser = 1
                    user_check.is_subject_teacher = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        'user_full_name': user_full_name, 
                        'user_account' : user_account,

                        'members': members,
                        # Response
                        'response' : "account created",
                    }

                    return render(request, 'admin-faculty-member-account.html', context)
                
                if user_account_input == "Academic Affairs":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.department = "Academic Affairs"
                    user_check.is_academic_affairs = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        'user_full_name': user_full_name, 
                        'user_account' : user_account,

                        'members': members,
                        # Response
                        'response' : "account created",
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Library":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.department = "Library"
                    user_check.is_library = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        'user_full_name': user_full_name, 
                        'user_account' : user_account,

                        'members': members,
                        # Response
                        'response' : "account created",
                    }

                    return render(request, 'admin-faculty-member-account.html', context)
                
                if user_account_input == "Research & Extension":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.department = "Research & Extension"
                    user_check.is_research_extension = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        'user_full_name': user_full_name, 
                        'user_account' : user_account,

                        'members': members,
                        # Response
                        'response' : "account created",
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

            else:
                print("password mismatch")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    'user_full_name': user_full_name, 
                    'user_account' : user_account,

                    # Form
                    'form': form,
                    'dit_head_exist' : dit_head_exist,

                    # Response
                    'response' : "password mismatch",
                }

                return render(request, 'admin-faculty-member-create-acc.html', context)

        else:
            print("User Exist")
            print(dit_head_exist)

            context = {
                # Topbar Start
                'user_full_name': user_full_name, 
                'user_account' : user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "username or email exist",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

    context = {
        # Topbar Start
        'user_full_name': user_full_name, 
        'user_account' : user_account,

        # Form
        'form': form,

        'dit_head_exist' : dit_head_exist,
        }
    return render(request, 'admin-faculty-member-create-acc.html', context)


# Admin - Faculty Member Individual Account Page
@login_required(login_url='index')
def adminFacultyMemberData(request, id):
    current_user = (request.user)
    currentpassword = (request.user.password)

    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    try:
        member_check = User.objects.get(username=id)
    except:
        return redirect('admin-faculty-member-acc')
    

    print(member_check.username)
    member_honorific = member_check.honorific
    member_username = member_check.username
    member_email = member_check.email
    member_first_name = member_check.first_name
    member_middle_name = member_check.middle_name
    member_last_name = member_check.last_name
    member_department = member_check.department

    context = {
        'user_full_name': user_full_name,
        'user_account' : user_account,

        'member_honorific': member_honorific,
        'member_username': member_username,
        'member_email': member_email,
        'member_first_name': member_first_name,
        'member_middle_name': member_middle_name,
        'member_last_name': member_last_name,
        'member_department': member_department,
        }
    
    if request.method == 'POST':
        honorific_list = ["Mr.", "Ms.", "Mrs.", "Engr.", "Dr.", "Dra."]
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", 'Library', 'Research & Extension']
        
        username_input = request.POST.get('username_input')
        email_input = request.POST.get('email_input')
        honorific_input = request.POST.get('honorific_input')
        first_name_input = request.POST.get('first_name_input')
        middle_name_input = request.POST.get('middle_name_input')
        last_name_input = request.POST.get('last_name_input')
        password_input = request.POST.get('password_input')

        if honorific_input != "default":
                pass

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'member_honorific': member_honorific,
                'member_username': member_username,
                'member_email': member_email,
                'member_first_name': member_first_name,
                'member_middle_name': member_middle_name,
                'member_last_name': member_last_name,
                'member_department': member_department,

                'response' : "choose honorific"
                }

            return render(request, 'admin-faculty-member-data.html', context)

        if "TUPC" in username_input:
                pass

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'member_honorific': member_honorific,
                'member_username': member_username,
                'member_email': member_email,
                'member_first_name': member_first_name,
                'member_middle_name': member_middle_name,
                'member_last_name': member_last_name,
                'member_department': member_department,

                'response' : "invalid username"
                }

            return render(request, 'admin-faculty-member-data.html', context)
        
        if "gsfe.tupcavite.edu.ph" in email_input:
            pass

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'member_honorific': member_honorific,
                'member_username': member_username,
                'member_email': member_email,
                'member_first_name': member_first_name,
                'member_middle_name': member_middle_name,
                'member_last_name': member_last_name,
                'member_department': member_department,

                'response' : "invalid email"
                }

            return render(request, 'admin-faculty-member-data.html', context)

        if member_check.password == password_input:

            member_check.honorific=honorific_input
            member_check.first_name=first_name_input.title()
            member_check.middle_name=middle_name_input.title()
            member_check.last_name=last_name_input.title()
            member_check.save()

            if member_check.username == username_input and member_check.email == email_input:

                members = User.objects.all().filter(is_faculty_member=1)
                
                context = {
                    'user_full_name': user_full_name,
                    'user_account' : user_account,

                    'members' : members,

                    'response' : "profile updated"
                    }

                return render(request, 'admin-faculty-member-account.html', context)

            if member_check.username != username_input and member_check.email == email_input:
                try:
                    User.objects.get(username=username_input)

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'members' : members,

                        'response' : "partial update username exist"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.username=username_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)
                    
                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,
                        'response' : "profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

            if member_check.username == username_input and member_check.email != email_input:
                
                try:
                    User.objects.get(email=email_input)

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'members' : members,

                        'response' : "partial update email exist"
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.email = email_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'members' : members,

                        'response' : "profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)
                
            if member_check.username != username_input and member_check.email != email_input:
                
                try:
                    User.objects.get(username=username_input)
                    User.objects.get(email=email_input)

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'members' : members,

                        'response' : "partial update username and email exist"
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.username=username_input
                    member_check.email=email_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    context = {
                        'user_full_name': user_full_name,
                        'user_account' : user_account,

                        'members' : members,

                        'response' : "profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

        else:
            context = {
                'user_full_name': user_full_name,
                'user_account' : user_account,

                'member_honorific': member_honorific,
                'member_username': member_username,
                'member_email': member_email,
                'member_first_name': member_first_name,
                'member_middle_name': member_middle_name,
                'member_last_name': member_last_name,
                'member_department': member_department,

                'response' : "incorrect password"
                }

            return render(request, 'admin-faculty-member-data.html', context)

    return render(request, 'admin-faculty-member-data.html', context)


# Admin - Faculty Member Change Password Process
@login_required(login_url='index')
def adminFacultyMemberChangePassword(request, id):
    current_user = (request.user)
    currentpassword = (request.user.password)

   # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"

    # Topbar End

    faculty_member_check = User.objects.get(username=id)
    currentpassword = faculty_member_check.password

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == currentpassword:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=faculty_member_check.username).update(password=new_password_input)

                    members = User.objects.all().filter(is_faculty_member=1)

                    member_check = User.objects.get(username=id)
                    
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,

                        'response' : 'sweet password changed success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                else:
                    members = User.objects.all().filter(is_faculty_member=1)

                    member_check = User.objects.get(username=id)
                    
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,

                        'response' : 'sweet confirm change password mismatch',
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

            else:
                member_check = User.objects.get(username=id)
                
                members = User.objects.all().filter(is_faculty_member=1)

                member_username = member_check.username
                member_full_name = member_check.first_name + " " + member_check.last_name

                context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'members' : members,

                'member_username': member_username,
                'member_full_name': member_full_name,

                    'response' : 'sweet same change password',
                }

                return render(request, 'admin-faculty-member-account.html', context)

        else:
            print("incorrect current password")
            members = User.objects.all().filter(is_faculty_member=1)

            member_check = User.objects.get(username=id)

            member_username = member_check.username
            member_full_name = member_check.first_name + " " + member_check.last_name

            context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'members' : members,

                'member_username': member_username,
                'member_full_name': member_full_name,

                'response' : 'sweet incorrect change current password',
                }

            return render(request, 'admin-faculty-member-account.html', context)

    return render(request, 'student-profile.html', context)


# Admin - Faculty Member Change User Account Process
@login_required(login_url='index')
def adminFacultyMemberChangeUserAccount(request, id):
    current_user = (request.user)
    currentpassword = (request.user.password)

    # Topbar Start
    user_middle_name = current_user.middle_name
    user_middle_initial = None

    user_full_name = None
    user_account = None

    if user_middle_name == "":
       user_full_name = current_user.first_name + " " + current_user.last_name

    else:
        user_middle_initial = user_middle_name[0]
        user_full_name = current_user.first_name + " " + user_middle_initial + ". " + current_user.last_name

    if current_user.is_student == 1:
        user_account = "Student"
     
    elif current_user.is_department_head == 1:
        user_account = "DIT Head"
    
    elif current_user.is_panel == 1:
        user_account = "Faculty Member"
    
    elif current_user.is_administrator == 1:
        user_account = "Administrator"
    # Topbar End

    try:
        member_check = User.objects.get(username=id)

    except:
        return redirect('admin-faculty-member-acc')

    print(member_check.department)
    
    if request.method == 'POST':
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", 'Library', 'Research & Extension']

        user_account_input = request.POST.get('user_account_input')
        current_password_input = request.POST.get('current_password_input')

        if user_account_input == "default":
            print("choose User Account") 

            members = User.objects.all().filter(is_faculty_member=1)
            
            member_username = member_check.username
            member_full_name = member_check.first_name + " " + member_check.last_name

            context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'members' : members,

                'member_username': member_username,
                'member_full_name': member_full_name,

                'response' : "sweet choose user account"
                }

            return render(request, 'admin-faculty-member-account.html', context)

        if user_account_input not in user_account_list:
            print("User Account not in list")

            members = User.objects.all().filter(is_faculty_member=1)
            
            member_username = member_check.username
            member_full_name = member_check.first_name + " " + member_check.last_name

            context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'members' : members,

                'member_username': member_username,
                'member_full_name': member_full_name,

                'response' : "sweet user account not in list"
                }

            return render(request, 'admin-faculty-member-account.html', context)

        if member_check.password == current_password_input:
            
            if member_check.department == user_account_input:

                members = User.objects.all().filter(is_faculty_member=1)

                member_check = User.objects.get(username=id)
                member_username = member_check.username
                member_full_name = member_check.first_name + " " + member_check.last_name
                member_department = member_check.department

                context = {
                    'user_full_name': user_full_name,
                    'user_account': user_account,

                    'members' : members,

                    'member_username': member_username,
                    'member_full_name': member_full_name,
                    'member_department': member_department,

                    'response' : 'sweet already',
                    }

                return render(request, 'admin-faculty-member-account.html', context)

            else:

                if user_account_input == "DIT Head":

                    member_check = User.objects.get(username=id)
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    member_check.department = user_account_input

                    member_check.is_department_head = 1
                    member_check.is_panel = 1
                    member_check.is_adviser = 1
                    member_check.is_subject_teacher = 1
                    member_check.is_academic_affairs = 0
                    member_check.is_library = 0
                    member_check.is_research_extension = 0
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,
                        'member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Faculty Member":

                    member_check = User.objects.get(username=id)
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    member_check.department = user_account_input

                    member_check.is_department_head = 0
                    member_check.is_panel = 1
                    member_check.is_adviser = 1
                    member_check.is_subject_teacher = 1
                    member_check.is_academic_affairs = 0
                    member_check.is_library = 0
                    member_check.is_research_extension = 0
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,
                        'member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Academic Affairs":

                    member_check = User.objects.get(username=id)
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    member_check.department = user_account_input

                    member_check.is_department_head = 0
                    member_check.is_panel = 0
                    member_check.is_adviser = 0
                    member_check.is_subject_teacher = 0
                    member_check.is_academic_affairs = 1
                    member_check.is_library = 0
                    member_check.is_research_extension = 0
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,
                        'member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Library":

                    member_check = User.objects.get(username=id)
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    member_check.department = user_account_input

                    member_check.is_department_head = 0
                    member_check.is_panel = 0
                    member_check.is_adviser = 0
                    member_check.is_subject_teacher = 0
                    member_check.is_academic_affairs = 0
                    member_check.is_library = 1
                    member_check.is_research_extension = 0
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,
                        'member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Research & Extension":

                    member_check = User.objects.get(username=id)
                    member_username = member_check.username
                    member_full_name = member_check.first_name + " " + member_check.last_name

                    member_check.department = user_account_input

                    member_check.is_department_head = 0
                    member_check.is_panel = 0
                    member_check.is_adviser = 0
                    member_check.is_subject_teacher = 0
                    member_check.is_academic_affairs = 0
                    member_check.is_library = 0
                    member_check.is_research_extension = 1
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'user_full_name': user_full_name,
                        'user_account': user_account,

                        'members' : members,

                        'member_username': member_username,
                        'member_full_name': member_full_name,
                        'member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)
        else:
            members = User.objects.all().filter(is_faculty_member=1)

            member_check = User.objects.get(username=id)
            member_username = member_check.username
            member_full_name = member_check.first_name + " " + member_check.last_name

            context = {
                'user_full_name': user_full_name,
                'user_account': user_account,

                'members' : members,

                'member_username': member_username,
                'member_full_name': member_full_name,

                'response' : 'sweet incorrect current password',
                }

            return render(request, 'admin-faculty-member-account.html', context)