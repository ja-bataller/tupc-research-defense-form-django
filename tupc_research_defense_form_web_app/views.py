from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from pyparsing import empty
from .forms import SignUpForm
from .models import *
# Import Date & Time
from datetime import date
# Import Docx and PDF Convert
from docx import Document
from docx2pdf import convert
from docx.shared import Inches
import qrcode
import os

today = date.today()
##########################################################################################################################

# Index / Log in Page
def index(request):

    if request.method == 'POST':
        # Get data from Front-end
        username_input_index_form = request.POST.get('username_input')
        password_input_index_form = request.POST.get('password_input')
        
        # Check if the user exist
        try:
            user_check = User.objects.get(username=username_input_index_form)
            
            # Check the password of the user if correct
            if user_check.password == password_input_index_form:
                print("The Password is correct")

                if user_check.is_student == 1:
                    print("User: Student")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect('student-dashboard')
                
                if user_check.is_administrator == 1:
                    print("User: Admin")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect('admin-dashboard')
                
                if user_check.is_department_head == 1:
                    print("User: DIT Head")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect('login-as')
                
                if user_check.is_panel == 1:
                    print("User: Panel")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect('login-as')

            else:
                print("The Password is incorrect.")

                context = {'response': "incorrect password"}
                return render(request, 'index.html', context)
        
        # If the user doesn't exist
        except:
            print("The User doesn't exist.")

            context = {'response': "user does not exist"}
            return render(request, 'index.html', context)

    return render(request, 'index.html')

#  Sign up Page
def signup(request):

    form = SignUpForm()

    suffix_list = ["", "Sr.", "Jr.","I","II","III","IV","V"]

    course = StudentCourseMajor.objects.all()
    subject_teachers = User.objects.all().filter(is_subject_teacher=1)

    course_list = []

    subject_teacher_list = []

    if not course:
        print("No Course Available")

        context = {
            'form': form,
            'response': "sweet incomplete form"}

        return render(request, 'signup.html', context)
    
    else:
        for course_abbr in course:
            course_list.append(course_abbr.course_major_abbr)


    if not subject_teachers:
        print("No Subject Teachers Available")

        context = {
            'form': form,
            'response': "sweet incomplete form"}

        return render(request, 'signup.html', context)
    
    else:
        for subject_teacher in subject_teachers:

            subject_teacher_full_name = None

            if subject_teacher.middle_name == "":
                subject_teacher_full_name =  subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.last_name +  " " + subject_teacher.suffix
                subject_teacher_list.append(subject_teacher_full_name)
            else:
                subject_teacher_full_name =  subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.middle_name[0] + ". " + subject_teacher.last_name +   " " + subject_teacher.suffix
                subject_teacher_list.append(subject_teacher_full_name)
    
        print("Available Course: ", course_list)
        print("Available Subject Teachers: ", subject_teacher_list)

        subject_teacher_list.sort()

    if request.method == "POST":
        form = SignUpForm(request.POST)

        suffix_input = request.POST.get('suffix_input')
        course_input = request.POST.get('course_input')
        subject_teacher_input = request.POST.get('subject_teacher_input')
        confirm_password = request.POST.get('confirm_password_input')

        if suffix_input not in suffix_list:

            context = {
                'form': form, 
                "course" : course,
                'subject_teachers' : subject_teachers,

                'response': "sweet invalid suffix"
            }

            return render(request, 'signup.html', context)

        if course_input == "default":

            context = {
                'form': form, 
                "course" : course,
                'subject_teachers' : subject_teachers,

                'response': "choose course"
            }

            return render(request, 'signup.html', context)

        if course_input not in course_list:

            context = {
                'form': form, 
                "course" : course,
                'subject_teachers' : subject_teachers,

                'response': "sweet invalid course"
            }

            return render(request, 'signup.html', context)

        if subject_teacher_input == "default":

            context = {
                'form': form, 
                "course" : course,
                'subject_teachers' : subject_teachers,

                'response': "choose subject teacher"
            }

            return render(request, 'signup.html', context)

        if subject_teacher_input not in course_list:

            context = {
                'form': form, 
                "course" : course,
                'subject_teachers' : subject_teachers,

                'response': "sweet invalid subject teacher"
            }

        if form.is_valid():
            print("Valid form")

            user = form.save(commit=False)

            user_username_input = user.username
            user_email_input = user.email

            # Check if the Username is already part of a group
            try:
                student_member_check = StudentGroupMember.objects.get(student_member_username=user_username_input)
                print("User exist")

                context = {
                    'form': form, 
                    "course" : course, 

                    'subject_teachers' : subject_teachers,
                    
                    "student_member_check_username" : student_member_check.student_member_username,
                    "student_member_check_name" : student_member_check.student_member_name,

                    'response': "sweet user exist",

                    }
                return render(request, 'signup.html', context)

            except:
                pass
            
            # Check if the Username is valid
            if "TUPC" in user_username_input:
                pass

            else:
                context = {
                    'form': form,
                    "course" : course, 
                    'subject_teachers' : subject_teachers,
                    'response': "invalid username"}
                return render(request, 'signup.html', context)
            
            if "gsfe.tupcavite.edu.ph" in user_email_input:
                pass

            else:
                context = {
                    'form': form,
                    "course" : course, 
                    'subject_teachers' : subject_teachers,
                    'response': "invalid email"}
                return render(request, 'signup.html', context)

            if user.password == confirm_password:
                print("Match password")

                user.save()

                user_check = User.objects.get(username=user.username)
                user_check.first_name = request.POST.get('first_name_input').title()
                user_check.middle_name = request.POST.get('middle_name_input').title()
                user_check.last_name = request.POST.get('last_name_input').title()
                user_check.suffix = request.POST.get('suffix_input')
                user_check.department = "Industrial Technology"
                user_check.is_student = 1
                user_check.save()

                course_data = StudentCourseMajor.objects.get(course_major_abbr=request.POST.get('course_input'))
                
                print(subject_teacher_input)
                subject_teacher_data = User.objects.get(username=subject_teacher_input)

                subject_teacher_full_name = None

                if subject_teacher_data.middle_name == "":
                    subject_teacher_full_name = subject_teacher_data.honorific + " " + subject_teacher_data.first_name + " " + subject_teacher_data.last_name + " " + subject_teacher_data.suffix
                
                else:
                    subject_teacher_full_name = subject_teacher_data.honorific + " " + subject_teacher_data.first_name + subject_teacher_data.middle_name[0] + ". " + subject_teacher_data.last_name + " " + subject_teacher_data.suffix

                student_leader = StudentLeader(
                    username = user_check.username,
                    email = user_check.email,

                    first_name = request.POST.get('first_name_input').title(),
                    middle_name = request.POST.get('middle_name_input').title(),
                    last_name = request.POST.get('last_name_input').title(),
                    suffix = suffix_input,

                    department = "Industrial Technology",
                    course = course_data.course,
                    major = course_data.major,
                    course_major_abbr = course_data.course_major_abbr,

                    bet3_subject_teacher_username = subject_teacher_data.username,
                    bet3_subject_teacher_name = subject_teacher_full_name,
                    bet3_status = "Ongoing",

                    current_subject = "BET-3"
                    )

                student_leader.save()

                login(request, user)
                return redirect('student-dashboard')

            else:
                print("Mismatch password")

                context = {'form': form,
                "course" : course, 
                'subject_teachers' : subject_teachers,
                'response': "password mismatch"}
                return render(request, 'signup.html', context)

        else:
            print("Invalid form")

            context = {
                'form': form, 
                "course" : course, 
                'subject_teachers' : subject_teachers,
                'response': "invalid form"}
            return render(request, 'signup.html', context)

    context = {
        'form': form, 
        'course' : course,
        'subject_teachers' : subject_teachers,
        }
    
    return render(request, 'signup.html', context)

# Log out
def logout_user(request):
    currently_loggedin_user = (request.user)

    if currently_loggedin_user.is_student == 1:
        panel_invitation_bet_3_path_1 = ('1-' + currently_loggedin_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')
        panel_invitation_bet_3_path_2 = ('2-' + currently_loggedin_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')
        panel_invitation_bet_3_path_3 = ('3-' + currently_loggedin_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')
        panel_invitation_bet_3_path_4 = ('4-' + currently_loggedin_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')
        panel_invitation_bet_3_path_5 = ('5-' + currently_loggedin_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')

        if os.path.isfile(panel_invitation_bet_3_path_1):
            os.remove(panel_invitation_bet_3_path_1)
            print("Panel Invitation BET-3 1 has been deleted")
        else:
            print("Panel Invitation BET-3 1 does not exist")
        
        if os.path.isfile(panel_invitation_bet_3_path_2):
            os.remove(panel_invitation_bet_3_path_2)
            print("Panel Invitation BET-3 2 has been deleted")
        else:
            print("Panel Invitation BET-3 2 does not exist")

        if os.path.isfile(panel_invitation_bet_3_path_3):
            os.remove(panel_invitation_bet_3_path_3)
            print("Panel Invitation BET-3 3 has been deleted")
        else:
            print("Panel Invitation BET-3 3 does not exist")

        
        if os.path.isfile(panel_invitation_bet_3_path_4):
            os.remove(panel_invitation_bet_3_path_4)
            print("Panel Invitation BET-3 4 has been deleted")
        else:
            print("Panel Invitation BET-3 4 does not exist")

        
        if os.path.isfile(panel_invitation_bet_3_path_5):
            os.remove(panel_invitation_bet_3_path_5)
            print("Panel Invitation BET-3 5 has been deleted")
        else:
            print("Panel Invitation BET-3 5 does not exist")

    logout(request)
    return redirect('index')


# Index / Log in Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_panel, login_url='index')
def login_as_user_accounts(request):
    currently_loggedin_user = (request.user)
    
    if currently_loggedin_user.is_department_head == 1:

        context = {
            'is_department_head' : "1",
        }
        return render(request, 'login-as-user-accounts.html', context)
    else:
        return render(request, 'login-as-user-accounts.html')

##########################################################################################################################

# Student - Dashboard Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentDashboard(request):
    current_user = (request.user)
    current_password = current_user.password

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Panel Invitation BET-3
    try:
        panel_invitation_bet3_check = PanelInvitation.objects.get(student_leader_username=current_user.username)


        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        "panel_invitation_bet3" : panel_invitation_bet3_check,
        }
        print("pass")
        return render(request, 'student-dashboard.html', context)
    except:
        pass
    
    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,
        }

    return render(request, 'student-dashboard.html', context)


# Student - Profile Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentProfile(request):
    current_user = (request.user)
    current_password = current_user.password

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Student Profile
    student = StudentLeader.objects.get(username=current_user)

    user_username = student.username
    user_first_name = student.first_name
    user_middle_name = student.middle_name
    user_last_name = student.last_name
    user_suffix = student.suffix
    user_email = student.email
    user_course = student.course_major_abbr
    course_name = student.course
    major_name = student.major


    context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'user_suffix': user_suffix,
                'user_course': user_course,  
                'course_name' : course_name,
                'major_name' : major_name,
                'username': user_username, 
                'user_email':user_email,
                }   

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == current_password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'user_first_name': user_first_name,
                        'user_middle_name' : user_middle_name,
                        'user_last_name' : user_last_name,
                        'user_course': user_course,  
                        'course_name' : course_name,
                        'major_name' : major_name,
                        'username': user_username, 
                        'user_email':user_email,

                        "response": "new password and confirm new password doesnt match"
                        }

                    return render(request, 'student-profile.html', context)

            else:
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'user_first_name': user_first_name,
                    'user_middle_name' : user_middle_name,
                    'user_last_name' : user_last_name,
                    'user_course': user_course,  
                    'course_name' : course_name,
                    'major_name' : major_name,
                    'username': user_username, 
                    'user_email':user_email,

                    "response": "current password and new password is same"
                    }

                return render(request, 'student-profile.html', context)

        else:
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                'user_first_name': user_first_name,
                'user_middle_name' : user_middle_name,
                'user_last_name' : user_last_name,
                'user_course': user_course,  
                'course_name' : course_name,
                'major_name' : major_name,
                'username': user_username, 
                'user_email':user_email, 

                "response": "current password is incorrect"
                }

            return render(request, 'student-profile.html', context)

    return render(request, 'student-profile.html', context)


# Student - Panel Invitation BET-3 Process
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentPanelInvitationBet3(request):
    current_user = (request.user)

    student_data = StudentLeader.objects.get(username=current_user.username)
    defense_dates = DefenseSchedule.objects.all().filter(username = student_data.bet3_subject_teacher_username , course = student_data.course_major_abbr)
    
    panel_members = User.objects.all().filter(is_panel=1)

    try:
        PanelInvitation.objects.get(student_leader_username=current_user)
        print("Panel Invitation - BET-3 Exist")
        return redirect('student-panel-invitation-bet3-form')

    except:
        pass

    try:
        dept_head_check = User.objects.get(is_department_head=1)
        pass

    except:
        print("No DIT Head")

        context = {
            'response' : "sweet no DIT Head"
        }

        return render(request, 'student-panel-invitation-bet-3-create.html', context)

    if not panel_members or panel_members.count() < 5:
            print("Incomplete Faculty Member")
            context = {
                'response' : "sweet inc panel"
            }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
    else:
        pass


    if not defense_dates:
            print("No Defense Schedule")
            context = {
                'response' : "sweet no defense schedule"
            }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
    else:
        pass

    print("Panel Conforme - BET-3 Create")
    return redirect('student-panel-invitation-bet3-create')

# Student - Panel Invitation Create Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentPanelInvitationBet3Create(request):
    current_user = (request.user)
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    student = StudentLeader.objects.get(username=current_user.username)

    defense_dates = DefenseSchedule.objects.all().filter(course=student.course_major_abbr, username = student.bet3_subject_teacher_username, status = "Available")

    defense_date_list = []

    suffix_list = ["", "Sr.", "Jr.","I","II","III","IV","V"]

    panel_members = User.objects.all().filter(is_panel=1)

    panel_list = []

    dept_head_name = None

    print(panel_members)

    # Check if there is DIT Head assigned.
    try:
        dept_head = User.objects.get(is_department_head=1)

        if dept_head.middle_name == "":
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.last_name + " " + dept_head.suffix
        else:
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.middle_name[0] + " " + dept_head.last_name + " " + dept_head.suffix

    except:
        print("No DIT Head")

        context = {
            'response' : "sweet no DIT Head"
        }

        return render(request, 'student-panel-invitation-bet-3-create.html', context)

    # Check if there is a Panel assigned.
    if not panel_members or panel_members.count() < 5:
            print("Incomplete Faculty Member")
            context = {
                'response' : "sweet inc panel"
            }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
    else:
        for panel in panel_members:
            panel_list.append(panel.username)
    
    for defense_date_id in defense_dates:
        defense_date_list.append(defense_date_id.id)


    if request.method == 'POST':
        student_username_1 = current_user.username
        student_first_name_1 = current_user.first_name
        student_middle_name_1 = current_user.middle_name
        student_last_name_1 = current_user.last_name
        student_suffix_1 = current_user.suffix

        student_username_2 = request.POST.get('student_username_2')
        student_first_name_2 = request.POST.get('student_first_name_2')
        student_middle_name_2 = request.POST.get('student_middle_name_2')
        student_last_name_2 = request.POST.get('student_last_name_2')
        student_suffix_2 = request.POST.get('student_suffix_2')

        student_username_3 = request.POST.get('student_username_3')
        student_first_name_3 = request.POST.get('student_first_name_3')
        student_middle_name_3 = request.POST.get('student_middle_name_3')
        student_last_name_3 = request.POST.get('student_last_name_3')
        student_suffix_3 = request.POST.get('student_suffix_3')

        student_username_4 = request.POST.get('student_username_4')
        student_first_name_4 = request.POST.get('student_first_name_4')
        student_middle_name_4 = request.POST.get('student_middle_name_4')
        student_last_name_4 = request.POST.get('student_last_name_4')
        student_suffix_4 = request.POST.get('student_suffix_4')

        student_username_5 = request.POST.get('student_username_5')
        student_first_name_5 = request.POST.get('student_first_name_5')
        student_middle_name_5 = request.POST.get('student_middle_name_5')
        student_last_name_5 = request.POST.get('student_last_name_5')
        student_suffix_5 = request.POST.get('student_suffix_5')

        research_title_1_input = request.POST.get('research_title_1_input').title()
        research_title_2_input = request.POST.get('research_title_2_input').title()
        research_title_3_input = request.POST.get('research_title_3_input').title()
        research_title_4_input = request.POST.get('research_title_4_input').title()
        research_title_5_input = request.POST.get('research_title_5_input').title()

        defense_schedule_input = int(request.POST.get('defense_schedule_input'))

        panel1_input = request.POST.get('panel1_input')
        panel2_input = request.POST.get('panel2_input')
        panel3_input = request.POST.get('panel3_input')
        panel4_input = request.POST.get('panel4_input')
        panel5_input = request.POST.get('panel5_input')

        if student_username_1 in (student_username_2, student_username_3, student_username_4, student_username_5):
            
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet same username'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
        
        # Check if the Student Member #1 exist
        try:
            group_member_check = StudentGroupMember.objects.get(student_member_username = student_username_1)

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'existing_member' : group_member_check,

                'response' : 'sweet group member exist'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)

        except:
            pass

        # If Student Member #2 is not none
        if student_username_2 != "":

            if student_username_2 in (student_username_1, student_username_3, student_username_4, student_username_5):
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same username'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if Group Member exists
            try:
                group_member_check = StudentGroupMember.objects.get(student_member_username = student_username_2)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_member' : group_member_check,

                    'response' : 'sweet group member exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        # If Student Member #3 is not none
        if student_username_3 != "":

            if student_username_3 in (student_username_1, student_username_2, student_username_4, student_username_5):
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same username'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Student Member #3 exist
            try:
                group_member_check = StudentGroupMember.objects.get(student_member_username = student_username_3)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_member' : group_member_check,

                    'response' : 'sweet group member exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        # If Student Member #4 is not none
        if student_username_4 != "":
            
            if student_username_4 in (student_username_1, student_username_2, student_username_3, student_username_5):
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same username'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Student Member #4 exist
            try:
                group_member_check = StudentGroupMember.objects.get(student_member_username = student_username_4)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_member' : group_member_check,

                    'response' : 'sweet group member exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        # If Student Member #5 is not none
        if student_username_5 != "":
            
            if student_username_5 in (student_username_1, student_username_2, student_username_3, student_username_4):
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same username'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            
            # Check if the Student Member #5 exist
            try:
                group_member_check = StudentGroupMember.objects.get(student_member_username = student_username_5)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_member' : group_member_check,

                    'response' : 'sweet group member exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        if student_suffix_1 in suffix_list or \
            student_suffix_2 in suffix_list or \
                student_suffix_3 in suffix_list or \
                    student_suffix_4 in suffix_list or \
                        student_suffix_5 in suffix_list:
            pass

        else:
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet invalid suffix'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
        
        if research_title_1_input in (research_title_2_input, research_title_3_input, research_title_4_input, research_title_5_input):
            
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet same research title'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
        
        # Check if the Research Title #1 exist
        try:
            research_title_check = ResearchTitle.objects.get(research_title = research_title_1_input)

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'existing_research_title' : research_title_check,

                'response' : 'sweet research title exist'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)

        except:
            pass

        if research_title_2_input != "":

            if research_title_2_input in (research_title_1_input, research_title_3_input, research_title_4_input, research_title_5_input):
            
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same research title'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Research Title #2 exist
            try:
                research_title_check = ResearchTitle.objects.get(research_title = research_title_2_input)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_research_title' : research_title_check,

                    'response' : 'sweet research title exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass
        
        if research_title_3_input != "":

            if research_title_3_input in (research_title_1_input, research_title_2_input, research_title_4_input, research_title_5_input):
            
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same research title'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Research Title #3 exist
            try:
                research_title_check = ResearchTitle.objects.get(research_title = research_title_3_input)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_research_title' : research_title_check,

                    'response' : 'sweet research title exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        if research_title_4_input != "":

            if research_title_4_input in (research_title_1_input, research_title_2_input, research_title_3_input, research_title_5_input):
            
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same research title'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Research Title #4 exist
            try:
                research_title_check = ResearchTitle.objects.get(research_title = research_title_4_input)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_research_title' : research_title_check,

                    'response' : 'sweet research title exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        if research_title_5_input != "":
            if research_title_5_input in (research_title_1_input, research_title_2_input, research_title_3_input, research_title_4_input):
            
                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'response' : 'sweet same research title'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            # Check if the Research Title #5 exist
            try:
                research_title_check = ResearchTitle.objects.get(research_title = research_title_5_input)

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'current_user':student,

                    'dept_head_name' : dept_head_name,

                    'panel_members' : panel_members,

                    'defense_dates': defense_dates,

                    'existing_research_title' : research_title_check,

                    'response' : 'sweet research title exist'
                    }

                return render(request, 'student-panel-invitation-bet-3-create.html', context)

            except:
                pass

        # Check if the Defense Schedule entered is valid.
        if defense_schedule_input not in defense_date_list:
            print("invalid date")
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet defense schedule doesnt exist'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
        
        # If entered panel member is not the same with other input field
        if panel1_input in (panel2_input, panel3_input, panel4_input, panel5_input) or \
            panel2_input in (panel1_input, panel3_input, panel4_input, panel5_input) or \
                 panel3_input in (panel1_input, panel2_input, panel4_input, panel5_input) or \
                     panel4_input in (panel1_input, panel2_input, panel3_input, panel5_input) or \
                         panel5_input in (panel1_input, panel2_input, panel3_input, panel4_input):

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet same panel'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)
        
        # Check if the Panel Member entered is valid.
        if panel1_input in panel_list or \
            panel2_input in panel_list or \
                panel3_input in panel_list or \
                    panel4_input in panel_list or \
                        panel5_input in panel_list:
            pass

        else:
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'current_user':student,

                'dept_head_name' : dept_head_name,

                'panel_members' : panel_members,

                'defense_dates': defense_dates,

                'response' : 'sweet invalid panel'
                }

            return render(request, 'student-panel-invitation-bet-3-create.html', context)

        ############## PANEL DATA ##############
        panel_data_1 = User.objects.get(username = panel1_input)
        panel_data_2 = User.objects.get(username = panel2_input)
        panel_data_3 = User.objects.get(username = panel3_input)
        panel_data_4 = User.objects.get(username = panel4_input)
        panel_data_5 = User.objects.get(username = panel5_input)

        panel_full_name_1 = None
        panel_full_name_2 = None
        panel_full_name_3 = None
        panel_full_name_4 = None
        panel_full_name_5 = None

        if panel_data_1.middle_name == "":
            panel_full_name_1 = panel_data_1.honorific + " " + panel_data_1.first_name + " " +  panel_data_1.last_name + " " + panel_data_1.suffix
        else:
            panel_full_name_1 = panel_data_1.honorific + " " + panel_data_1.first_name + " " +  panel_data_1.middle_name[0] + ". " +  panel_data_1.last_name + " " + panel_data_1.suffix


        if panel_data_2.middle_name == "":
            panel_full_name_2 = panel_data_2.honorific + " " + panel_data_2.first_name + " " +  panel_data_2.last_name + " " + panel_data_2.suffix
        else:
            panel_full_name_2 = panel_data_2.honorific + " " + panel_data_2.first_name + " " +  panel_data_2.middle_name[0] + ". " +  panel_data_2.last_name + " " + panel_data_2.suffix


        if panel_data_3.middle_name == "":
            panel_full_name_3 = panel_data_3.honorific + " " + panel_data_3.first_name + " " +  panel_data_3.last_name + " " + panel_data_3.suffix
        else:
            panel_full_name_3 = panel_data_3.honorific + " " + panel_data_3.first_name + " " +  panel_data_3.middle_name[0] + ". " +  panel_data_3.last_name + " " + panel_data_3.suffix
        

        if panel_data_4.middle_name == "":
            panel_full_name_4 = panel_data_4.honorific + " " + panel_data_4.first_name + " " +  panel_data_4.last_name + " " + panel_data_4.suffix
        else:
            panel_full_name_4 = panel_data_4.honorific + " " + panel_data_4.first_name + " " +  panel_data_4.middle_name[0] + ". " +  panel_data_4.last_name + " " + panel_data_4.suffix


        if panel_data_5.middle_name == "":
            panel_full_name_5 = panel_data_5.honorific + " " + panel_data_5.first_name + " " +  panel_data_5.last_name + " " + panel_data_5.suffix
        else:
            panel_full_name_5 = panel_data_5.honorific + " " + panel_data_5.first_name + " " +  panel_data_5.middle_name[0] + ". " +  panel_data_5.last_name + " " + panel_data_5.suffix
        ############## PANEL DATA ##############


        ############## STUDENT DATA ##############
        student_leader_data = StudentLeader.objects.get(username = current_user.username)

        student_full_name_1 = None
        student_full_name_2 = None
        student_full_name_3 = None
        student_full_name_4 = None
        student_full_name_5 = None

        course_short = student_leader_data.course.replace("Engineering", "Eng.")

        if student_middle_name_1 == "":
            student_full_name_1 = current_user.last_name + " " + current_user.suffix + ', ' + current_user.first_name 
        else:
            student_full_name_1 =  current_user.last_name + " " + current_user.suffix + ', ' + current_user.first_name + " " +  current_user.middle_name[0] + "." 

        if student_middle_name_2 == "":
            student_full_name_2 = student_last_name_2 + " " + student_suffix_2 + ', ' + student_first_name_2 + " "
        else:
            student_full_name_2 = student_last_name_2 + " " +  student_suffix_2 + ", " +  student_first_name_2 + " " + student_middle_name_2[0] + "."

        if student_middle_name_3 == "":
            student_full_name_3 = student_last_name_3 + " " + student_suffix_3 + ', ' + student_first_name_3 + " "
        else:
            student_full_name_3 = student_last_name_3 + " " +  student_suffix_3 + ", " +  student_first_name_3 + " " + student_middle_name_3[0] + "."
        
        if student_middle_name_4 == "":
            student_full_name_4 = student_last_name_4 + " " + student_suffix_4 + ', ' + student_first_name_4 + " "
        else:
            student_full_name_4 = student_last_name_4 + " " +  student_suffix_4 + ", " +  student_first_name_4 + " " + student_middle_name_4[0] + "."

        if student_middle_name_5 == "":
            student_full_name_5 = student_last_name_5 + " " + student_suffix_5 + ', ' + student_first_name_5 + " "
        else:
            student_full_name_5 = student_last_name_5 + " " +  student_suffix_5 + ", " +  student_first_name_5 + " " + student_middle_name_5[0] + "."
        ############## STUDENT DATA ##############

        ############## DEFENSE SCHEDULE DATA ##############
        defense_schedule_data = DefenseSchedule.objects.get(id=defense_schedule_input)
        ############## DEFENSE SCHEDULE DATA ##############

       
        student_leader_username = current_user.username

        dit_head_name = dept_head_name.title()
        dit_head_response = "Pending"
        dit_head_response_date = None

        panel_member_username_1 = panel_data_1.username
        panel_member_name_1 = panel_full_name_1.title()
        panel_member_response_1 = "On Hold"
        panel_member_response_date_1 = None

        panel_member_username_2 = panel_data_2.username
        panel_member_name_2 = panel_full_name_2.title()
        panel_member_response_2 = "On Hold"
        panel_member_response_date_2 = None

        panel_member_username_3 = panel_data_3.username
        panel_member_name_3 = panel_full_name_3.title()
        panel_member_response_3 = "On Hold"
        panel_member_response_date_3 = None

        panel_member_username_4 = panel_data_4.username
        panel_member_name_4 = panel_full_name_4.title()
        panel_member_response_4 = "On Hold"
        panel_member_response_date_4 = None

        panel_member_username_5 = panel_data_5.username
        panel_member_name_5 = panel_full_name_5.title()
        panel_member_response_5 = "On Hold"
        panel_member_response_date_5 = None

        student_member_username_1 = current_user.username
        student_member_name_1 = student_full_name_1.title()

        student_member_username_2 = student_username_2
        student_member_name_2 = student_full_name_2.title()

        student_member_username_3 = student_username_3
        student_member_name_3 = student_full_name_3.title()

        student_member_username_4 = student_username_4
        student_member_name_4 = student_full_name_4.title()

        student_member_username_5 = student_username_5
        student_member_name_5 = student_full_name_5.title()

        course = course_short
        major = student_leader_data.major
        course_major_abbr = student_leader_data.course_major_abbr

        research_title_1 = research_title_1_input.title()
        research_title_2 = research_title_2_input.title()
        research_title_3 = research_title_3_input.title()
        research_title_4 = research_title_4_input.title()
        research_title_5 = research_title_5_input.title()

        form_date_submitted = today.strftime("%B %d, %Y")

        defense_date = defense_schedule_data.date
        defense_start_time = defense_schedule_data.start_time
        defense_end_time =  defense_schedule_data.end_time
        form_status = "Incomplete"

        print(student_leader_username)

        print(dit_head_name)
        print(dit_head_response)
        print(dit_head_response_date)

        print(panel_member_username_1)
        print(panel_member_name_1)
        print(panel_member_response_1)
        print(panel_member_response_date_1)

        print(panel_member_username_2)
        print(panel_member_name_2)
        print(panel_member_response_2)
        print(panel_member_response_date_2)

        print(panel_member_username_3)
        print(panel_member_name_3)
        print(panel_member_response_3)
        print(panel_member_response_date_3)

        print(panel_member_username_4)
        print(panel_member_name_4)
        print(panel_member_response_4)
        print(panel_member_response_date_4)

        print(panel_member_username_5)
        print(panel_member_name_5)
        print(panel_member_response_5)
        print(panel_member_response_date_5)

        print(student_member_username_1)
        print(student_member_name_1)

        print(student_member_username_2)
        print(student_member_name_2)

        print(student_member_username_3)
        print(student_member_name_3)

        print(student_member_username_4)
        print(student_member_name_4)

        print(student_member_username_5)
        print(student_member_name_5)

        print(course)
        print(major)
        print(course_major_abbr)

        print(research_title_1)
        print(research_title_2)
        print(research_title_3)
        print(research_title_4)
        print(research_title_5)

        print(form_date_submitted)

        print(defense_date)
        print(defense_start_time)
        print(defense_end_time)
        print(form_status)

        ############## Student Leader ##############
        student_leader_status = StudentLeader.objects.get(username=current_user.username)
        student_leader_status.defense_status = "Title Defense"
        student_leader_status.save()
        ############## Student Leader ##############

        ############## PANEL INVITATION ##############
        panel_invitation = PanelInvitation(
            student_leader_username = student_leader_username,

            dit_head_name = dit_head_name,
            dit_head_response = dit_head_response,

            panel_member_username_1 = panel_member_username_1,
            panel_member_name_1 = panel_member_name_1,
            panel_member_response_1 = panel_member_response_1,

            panel_member_username_2 = panel_member_username_2,
            panel_member_name_2 = panel_member_name_2,
            panel_member_response_2 = panel_member_response_2,

            panel_member_username_3 = panel_member_username_3,
            panel_member_name_3 = panel_member_name_3,
            panel_member_response_3 = panel_member_response_3,

            panel_member_username_4  = panel_member_username_4,
            panel_member_name_4 = panel_member_name_4,
            panel_member_response_4 = panel_member_response_4,

            panel_member_username_5 = panel_member_username_5,
            panel_member_name_5 = panel_member_name_5,
            panel_member_response_5 = panel_member_response_5,

            student_member_username_1 = student_member_username_1, 
            student_member_name_1 = student_member_name_1,

            student_member_username_2 = student_member_username_2, 
            student_member_name_2 = student_member_name_2,

            student_member_username_3 = student_member_username_3, 
            student_member_name_3 = student_member_name_3,

            student_member_username_4 = student_member_username_4, 
            student_member_name_4 = student_member_name_4,

            student_member_username_5 = student_member_username_5, 
            student_member_name_5 = student_member_name_5,

            course = course_short,
            major = major,
            course_major_abbr = course_major_abbr,

            research_title_1 = research_title_1,
            research_title_2 = research_title_2,
            research_title_3 = research_title_3,
            research_title_4 = research_title_4,
            research_title_5 = research_title_5,

            form_date_submitted = form_date_submitted,

            defense_date = defense_date,
            defense_start_time = defense_start_time,
            defense_end_time = defense_end_time,

            form_status = form_status,
        )
        panel_invitation.save()
        ############## PANEL INVITATION ##############

        ############## Defense Schedule ##############
        defense_schedule = DefenseSchedule.objects.get(id=defense_schedule_input)
        defense_schedule.student_leader_username = current_user.username
        defense_schedule.student_leader_name = student_full_name_1
        defense_schedule.status = "Reserved"
        defense_schedule.save()
        ############## Defense Schedule ##############

        ############## Research Title ##############
        research_title_1 = ResearchTitle(
            research_title = research_title_1,
            course = student_leader_data.course,
            major = student_leader_data.major,
            student_leader_username = student_leader_data.username,
            student_leader_name = student_full_name_1,
            course_major_abbr = course_major_abbr,
            date_submitted = form_date_submitted
        )
        research_title_1.save()

        if research_title_2 != "":
            research_title_2 = ResearchTitle(
                research_title = research_title_2,
                course = student_leader_data.course,
                major = student_leader_data.major,
                student_leader_username = student_leader_data.username,
                student_leader_name = student_full_name_1,
                course_major_abbr = course_major_abbr,
                date_submitted = form_date_submitted
            )
            research_title_2.save()

        if research_title_3 != "":
            research_title_3 = ResearchTitle(
                research_title = research_title_3,
                course = student_leader_data.course,
                major = student_leader_data.major,
                student_leader_username = student_leader_data.username,
                student_leader_name = student_full_name_1,
                course_major_abbr = course_major_abbr,
                date_submitted = form_date_submitted
            )
            research_title_3.save()

        if research_title_4 != "":
            research_title_4 = ResearchTitle(
            research_title = research_title_4,
            course = student_leader_data.course,
            major = student_leader_data.major,
            student_leader_username = student_leader_data.username,
            student_leader_name = student_full_name_1,
            course_major_abbr = course_major_abbr,
            date_submitted = form_date_submitted
        )
            research_title_4.save()

        if research_title_5 != "":
            research_title_5 = ResearchTitle(
                research_title = research_title_5,
                course = student_leader_data.course,
                major = student_leader_data.major,
                student_leader_username = student_leader_data.username,
                student_leader_name = student_full_name_1,
                course_major_abbr = course_major_abbr,
                date_submitted = form_date_submitted
            )
            research_title_5.save()
        ############## Research Title ##############

        ############## Group Members ##############
        if student_member_username_2 != "":
            group_member_2 = StudentGroupMember(
                student_leader_name = student_member_name_1,
                student_leader_username = student_leader_data.username,
                
                student_member_username = student_member_username_2,
                student_member_name = student_member_name_2,

                course = student_leader_data.course,
                major = student_leader_data.major,
                course_major_abbr = course_major_abbr,
            )
            group_member_2.save()

        if student_member_username_3 != "":
            group_member_3 = StudentGroupMember(
                student_leader_name = student_member_name_1,
                student_leader_username = student_leader_data.username,
                
                student_member_username = student_member_username_3,
                student_member_name = student_member_name_3,

                course = student_leader_data.course,
                major = student_leader_data.major,
                course_major_abbr = course_major_abbr,
            )
            group_member_3.save()

        if student_member_username_4 != "":
            group_member_4 = StudentGroupMember(
                student_leader_name = student_member_name_1,
                student_leader_username = student_leader_data.username,
                
                student_member_username = student_member_username_4,
                student_member_name = student_member_name_4,

                course = student_leader_data.course,
                major = student_leader_data.major,
                course_major_abbr = course_major_abbr,
            )
            group_member_4.save()

        if student_member_username_5 != "":
            group_member_5 = StudentGroupMember(
                student_leader_name = student_member_name_1,
                student_leader_username = student_leader_data.username,
                
                student_member_username = student_member_username_5,
                student_member_name = student_member_name_5,

                course = student_leader_data.course,
                major = student_leader_data.major,
                course_major_abbr = course_major_abbr,
            )
            group_member_5.save()
        ############## Group Members ##############


        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        'response': "sweet panel invitation bet-3 success",
        }
        return render(request, 'student-dashboard.html', context)

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        'current_user':student,

        'dept_head_name' : dept_head_name,

        'panel_members' : panel_members,

        'defense_dates': defense_dates,
        }

    return render(request, 'student-panel-invitation-bet-3-create.html', context)

# Student - Panel Invitation Form Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentPanelInvitationBet3Form(request):
    current_user = (request.user)
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    try:
        user_panel_invitation = PanelInvitation.objects.get(student_leader_username = current_user.username)
    
    except:
        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,
        }

        return render(request, 'student-dashboard.html', context)
    
    panel_list = []
    panel_response = []
    panel_date_response = []

    if user_panel_invitation.panel_member_name_1 != "" and user_panel_invitation.panel_member_response_date_1:
        panel_list.append(user_panel_invitation.panel_member_name_1)
        panel_response.append(user_panel_invitation.panel_member_response_1)
        panel_date_response.append(user_panel_invitation.panel_member_response_date_1)
    
    if user_panel_invitation.panel_member_name_2 != "" and user_panel_invitation.panel_member_response_date_2:
        panel_list.append(user_panel_invitation.panel_member_name_2)
        panel_response.append(user_panel_invitation.panel_member_response_2)
        panel_date_response.append(user_panel_invitation.panel_member_response_date_2)

    if user_panel_invitation.panel_member_name_3 != "" and user_panel_invitation.panel_member_response_date_3:
        panel_list.append(user_panel_invitation.panel_member_name_3)
        panel_response.append(user_panel_invitation.panel_member_response_3)
        panel_date_response.append(user_panel_invitation.panel_member_response_date_3)

    if user_panel_invitation.panel_member_name_4 != "" and user_panel_invitation.panel_member_response_date_4:
        panel_list.append(user_panel_invitation.panel_member_name_4)
        panel_response.append(user_panel_invitation.panel_member_response_4)
        panel_date_response.append(user_panel_invitation.panel_member_response_date_4)

    if user_panel_invitation.panel_member_name_5 != "" and user_panel_invitation.panel_member_response_date_5:
        panel_list.append(user_panel_invitation.panel_member_name_5)
        panel_response.append(user_panel_invitation.panel_member_response_5)
        panel_date_response.append(user_panel_invitation.panel_member_response_date_5)

    print(panel_list)
    print(panel_date_response)

    student_member_list = [user_panel_invitation.student_member_name_1, user_panel_invitation.student_member_name_2, user_panel_invitation.student_member_name_3, user_panel_invitation.student_member_name_4, user_panel_invitation.student_member_name_5]
    student_member_list.sort()

    # Generate PDF Form
    if request.method == "POST":
        file_count = 1
        for i in range(len(panel_list)):

            doc = Document('static/forms/1-PANEL-INVITATION.docx')

            student_table = doc.tables[1]
            qr_code_box = doc.tables[2]
            response_table = doc.tables[3]

            student_table.cell(1, 0).paragraphs[0].runs[0].text = student_member_list[0]
            student_table.cell(2, 0).paragraphs[0].runs[0].text = student_member_list[1]
            student_table.cell(3, 0).paragraphs[0].runs[0].text = student_member_list[2]
            student_table.cell(4, 0).paragraphs[0].runs[0].text = student_member_list[3]
            student_table.cell(5, 0).paragraphs[0].runs[0].text = student_member_list[4]

            student_table.cell(1, 2).paragraphs[0].runs[0].text = user_panel_invitation.course
            student_table.cell(1, 4).paragraphs[0].runs[0].text = user_panel_invitation.major

            if user_panel_invitation.student_member_username_2 == "":
                student_table.cell(2, 2).paragraphs[0].runs[0].text = ""
                student_table.cell(2, 4).paragraphs[0].runs[0].text = ""
            else:
                student_table.cell(2, 2).paragraphs[0].runs[0].text = user_panel_invitation.course
                student_table.cell(2, 4).paragraphs[0].runs[0].text = user_panel_invitation.major
                
                
            if user_panel_invitation.student_member_username_3 == "":
                student_table.cell(3, 2).paragraphs[0].runs[0].text = ""
                student_table.cell(3, 4).paragraphs[0].runs[0].text = ""
    
            else:
                student_table.cell(3, 2).paragraphs[0].runs[0].text = user_panel_invitation.course
                student_table.cell(3, 4).paragraphs[0].runs[0].text = user_panel_invitation.major
                
                
            if  user_panel_invitation.student_member_username_4 == "":
                student_table.cell(4, 2).paragraphs[0].runs[0].text = ""
                student_table.cell(4, 4).paragraphs[0].runs[0].text = ""
            else:
                student_table.cell(4, 2).paragraphs[0].runs[0].text = user_panel_invitation.course
                student_table.cell(4, 4).paragraphs[0].runs[0].text = user_panel_invitation.major
                
                
            if  user_panel_invitation.student_member_username_5 == "":
                student_table.cell(5, 2).paragraphs[0].runs[0].text = ""
                student_table.cell(5, 4).paragraphs[0].runs[0].text = ""
            else:
                student_table.cell(5, 2).paragraphs[0].runs[0].text = user_panel_invitation.course
                student_table.cell(5, 4).paragraphs[0].runs[0].text = user_panel_invitation.major
                
            doc.paragraphs[1].runs[1].text = user_panel_invitation.form_date_submitted
            doc.paragraphs[2].runs[0].text = panel_list[i]
            doc.paragraphs[5].runs[1].text = panel_list[i]

            doc.paragraphs[11].runs[1].text = user_panel_invitation.research_title_1
            doc.paragraphs[12].runs[1].text = user_panel_invitation.research_title_2
            doc.paragraphs[13].runs[1].text = user_panel_invitation.research_title_3
            doc.paragraphs[14].runs[1].text = user_panel_invitation.research_title_4
            doc.paragraphs[15].runs[1].text = user_panel_invitation.research_title_5

            doc.paragraphs[17].runs[1].text =  user_panel_invitation.defense_date
            doc.paragraphs[17].runs[3].text =  user_panel_invitation.defense_start_time
            doc.paragraphs[17].runs[5].text =  user_panel_invitation.defense_end_time
            doc.paragraphs[22].runs[0].text =  user_panel_invitation.dit_head_name

            response_table.cell(0, 9).paragraphs[0].runs[0].text = panel_date_response[i]

            if panel_response[i] == "accepted":
                response_table.cell(0, 2).paragraphs[0].runs[0].text = '✓'
                response_table.cell(0, 5).paragraphs[0].runs[0].text = ''

            else:
                response_table.cell(0, 2).paragraphs[0].runs[0].text = ''
                response_table.cell(0, 5).paragraphs[0].runs[0].text = '✓'

            print(student_table.cell(1, 0).text)
            print(student_table.cell(2, 0).text)
            print(student_table.cell(3, 0).text)
            print(student_table.cell(4, 0).text)
            print(student_table.cell(5, 0).text)

            print(student_table.cell(1, 2).text)
            print(student_table.cell(2, 2).text)
            print(student_table.cell(3, 2).text)
            print(student_table.cell(4, 2).text)
            print(student_table.cell(5, 2).text)

            print(student_table.cell(1, 4).text)
            print(student_table.cell(2, 4).text)
            print(student_table.cell(3, 4).text)
            print(student_table.cell(4, 4).text)
            print(student_table.cell(5, 4).text)


            print(doc.paragraphs[1].runs[1].text) # Date Submitted
            print(doc.paragraphs[2].runs[0].text) # Receiver 1
            print(doc.paragraphs[5].runs[1].text) # Receiver 2

            print(doc.paragraphs[11].runs[1].text) # Research Title 1
            print(doc.paragraphs[12].runs[1].text) # Research Title 2
            print(doc.paragraphs[13].runs[1].text) # Research Title 3
            print(doc.paragraphs[14].runs[1].text) # Research Title 4
            print(doc.paragraphs[15].runs[1].text) # Research Title 5

            print(doc.paragraphs[17].runs[1].text) # Defense Date
            print(doc.paragraphs[17].runs[3].text) # Defense Time Start
            print(doc.paragraphs[17].runs[5].text) # Defense Time End
            print(doc.paragraphs[22].runs[0].text) # DIT Head Name
            print(response_table.cell(0, 9).text) # Panel Date Response

            img = qrcode.make('DIT Head: ' + user_panel_invitation.dit_head_name + '\n DIT Head Date Response: ' + user_panel_invitation.dit_head_response_date + "\n Panel Member Name: " + panel_list[i] + "\n Panel Member Date Response: " + panel_date_response[i] + "\n Form Date Submitted: " + user_panel_invitation.form_date_submitted)
            type(img) 
            img.save(str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET-3.png')

            # INSERT IMAGE
            qr_code = qr_code_box.cell(0, 0).add_paragraph()
            qr_code_run = qr_code.add_run()
            qr_code_run.add_picture(str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET-3.png',width=Inches(1), height=Inches(1))
            # qr_code_run.alignment=WD_ALIGN_PARAGRAPH.CENTER

            doc.save(str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET3-NEW.docx')
            convert(str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET3-NEW.docx')
            os.startfile(str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET3-NEW.pdf')

            qr_code_path = (str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET-3.png')
            if os.path.isfile(qr_code_path):
                os.remove(qr_code_path)
                print("QR Code has been deleted")
            else:
                print("QR Code does not exist")


            panel_invitation_bet_3_path = (str(file_count) + '-' + current_user.username + '-PANEL-CONFORME-BET3-NEW.docx')

            if os.path.isfile(panel_invitation_bet_3_path):
                os.remove(panel_invitation_bet_3_path)
                print("Panel Invitation BET-3 has been deleted")
            else:
                print("Panel Invitation BET-3 does not exist")
            
            i + 1
            file_count = file_count + 1
        
        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        'user_panel_invitation' : user_panel_invitation,

        'response' : "sweet downloaded"
        }

        return render(request, 'student-panel-invitation-bet-3-form.html', context)

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        'user_panel_invitation' : user_panel_invitation,
        }

    return render(request, 'student-panel-invitation-bet-3-form.html', context)

# Student - Panel Conforme BET-3 Process
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_student, login_url='index')
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
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentPanelConformeBet3Create(request):
    current_user = (request.user)
    current_password = current_user.password

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    user_middle_name = current_user.middle_name
    user_middle_initial = None
    user_course = current_user.course
    
    panel_member_check_list = []
    panel_members = User.objects.all().filter(is_panel=1)

    for panel_member in panel_members:
        panel_member_check_list.append(panel_member.username)

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

        # Get Student member 1 Username
        student1_username_input = current_user.username
        print("Student Username 1 =", student1_username_input)
        
        # Get Student Member 2 Name
        student2_input = request.POST.get('student2_input')
        print("Student 2 =", student2_input)

        # Get Student member 2 Username
        student2_username_input = request.POST.get('student2_username_input')
        print("Student Username 2 =", student2_username_input)

        # Get Student Member 3 Name
        student3_input = request.POST.get('student3_input')
        print("Student 3 =", student3_input)

        # Get Student member 3 Username
        student3_username_input = request.POST.get('student3_username_input')
        print("Student Username 3 =", student3_username_input)

        # Get Student Member 4 Name
        student4_input = request.POST.get('student4_input')
        print("Student 4 =", student4_input)

        # Get Student member 4 Username
        student4_username_input = request.POST.get('student4_username_input')
        print("Student Useranme 4 =", student4_username_input)

        # Get Student Member 5 Name
        student5_input = request.POST.get('student5_input')
        print("Student 5 =", student5_input)

        # Get Student member 5 Username
        student5_username_input = request.POST.get('student5_username_input')
        print("Student Username 5 =", student5_username_input)

        # Check if Student Member 2 has an account
        try:
            student_username_check = User.objects.get(username=student2_username_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'username_exist': student2_username_input,
                    'response' : "sweet student member exist 2"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')
        except:
            pass
        
        # Check if Student Member 3 has an account
        try:
            student_username_check = User.objects.get(username=student3_username_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'username_exist': student3_username_input,
                    'response' : "sweet student member exist 3"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')
        except:
            pass
        
        if not student4_username_input:
            print("No Group Member 4")
            pass

        else:
            #  If Student ID No. is invalid
            if "TUPC" not in student4_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'response' : "username invalid"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')
            
            # If Student ID No. is the same with the others
            if student1_username_input == student4_username_input or student2_username_input == student4_username_input or student3_username_input == student4_username_input or student4_username_input == student1_username_input or student4_username_input == student2_username_input or student4_username_input == student3_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'response' : "username same"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')

            # Check if Student Member 4 has an account
            try:
                student_username_check = User.objects.get(username=student4_username_input)

                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'username_exist': student4_username_input,
                        'response' : "sweet student member exist 4"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')
            except:
                pass

        if not student5_username_input:
            print("No Group Member 5")
            pass

        else:
            # If Student ID No. is invalid.
            if "TUPC" not in student5_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'response' : "username invalid"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')

            # If Student ID No. is the same with the others
            if student1_username_input == student5_username_input or student2_username_input == student5_username_input or student3_username_input == student5_username_input or student4_username_input == student5_username_input or student5_username_input == student1_username_input or student5_username_input == student2_username_input or student5_username_input == student3_username_input or student5_username_input == student4_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'response' : "username same"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')
            
            # Check if Student Member 5 has an account
            try:
                student_username_check = User.objects.get(username=student5_username_input)

                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'dept_head_name': dept_head_name,

                        'panel_check' : panel_check,

                        'leader_member_name' : leader_member_name_2,
                        'leader_member_username' : current_user.username,

                        'course_name' : course_name,
                        'major_name' : major_name,

                        'username_exist': student5_username_input,
                        'response' : "sweet student member exist 5"
                        }

                    return render(request, 'student-panel-conforme-bet-3-create.html', context)

                except:
                    return redirect('student-dashboard')
            except:
                pass

        # If the Student already has a Panel Conform BET-3
        try:
            PanelConformeBET3.objects.get(student_leader_username=current_user.username)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

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

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

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

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "choose 5 panel"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # If Panel Name input is the same with the other Panel Name Input
        if panel1_input == panel2_input or panel1_input == panel3_input or panel1_input == panel4_input or panel1_input == panel5_input or panel2_input == panel1_input or panel2_input == panel3_input or panel2_input == panel4_input or panel2_input == panel5_input or panel3_input == panel1_input or panel3_input == panel2_input or panel3_input == panel4_input or panel3_input == panel5_input or panel4_input == panel1_input or panel4_input == panel2_input or panel4_input == panel3_input or panel4_input == panel5_input or panel5_input == panel1_input or panel5_input == panel2_input or panel5_input == panel3_input or panel5_input == panel4_input: 
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "same panel"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # If Panel Name input is not in the Panel Member List
        if panel1_input not in panel_member_check_list or panel2_input not in panel_member_check_list or panel3_input not in panel_member_check_list or panel4_input not in panel_member_check_list or panel5_input not in panel_member_check_list: 
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "sweet panel not in the list"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        # If Student ID No. is invalid
        if "TUPC" not in student1_username_input or "TUPC" not in student2_username_input or "TUPC" not in student3_username_input:
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "username invalid"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')
        
        # If Student ID No. is the same with the others
        if student1_username_input == student2_username_input or student1_username_input == student3_username_input or student2_username_input == student1_username_input or student2_username_input == student3_username_input or student3_username_input == student1_username_input or student3_username_input == student2_username_input:
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'dept_head_name': dept_head_name,

                    'panel_check' : panel_check,

                    'leader_member_name' : leader_member_name_2,
                    'leader_member_username' : current_user.username,

                    'course_name' : course_name,
                    'major_name' : major_name,

                    'response' : "username same"
                    }

                return render(request, 'student-panel-conforme-bet-3-create.html', context)

            except:
                return redirect('student-dashboard')

        panel_check_1 = User.objects.get(username=panel1_input)
        panel_check_2 = User.objects.get(username=panel2_input)
        panel_check_3 = User.objects.get(username=panel3_input)
        panel_check_4 = User.objects.get(username=panel4_input)
        panel_check_5 = User.objects.get(username=panel5_input)

        panel_member_full_name_1 = None
        panel_member_full_name_2 = None
        panel_member_full_name_3 = None
        panel_member_full_name_4 = None
        panel_member_full_name_5 = None

        if panel_check_1.middle_name == "":
            panel_member_full_name_1 = panel_check_1.first_name + " " + panel_check_1.last_name
        else:
            panel_member_full_name_1 = panel_check_1.first_name + " " + panel_check_1.middle_name[0] + ". " + panel_check_1.last_name

        if panel_check_2.middle_name == "":
            panel_member_full_name_2 = panel_check_2.first_name + " " + panel_check_2.last_name
        else:
            panel_member_full_name_2 = panel_check_2.first_name + " " + panel_check_2.middle_name[0] + ". " + panel_check_2.last_name

        if panel_check_3.middle_name == "":
            panel_member_full_name_3 = panel_check_3.first_name + " " + panel_check_3.last_name
        else:
            panel_member_full_name_3 = panel_check_3.first_name + " " + panel_check_3.middle_name[0] + ". " + panel_check_3.last_name

        if panel_check_4.middle_name == "":
            panel_member_full_name_4 = panel_check_4.first_name + " " + panel_check_4.last_name
        else:
            panel_member_full_name_4 = panel_check_4.first_name + " " + panel_check_4.middle_name[0] + ". " + panel_check_4.last_name
        
        if panel_check_5.middle_name == "":
            panel_member_full_name_5 = panel_check_5.first_name + " " + panel_check_5.last_name
        else:
            panel_member_full_name_5 = panel_check_5.first_name + " " + panel_check_5.middle_name[0] + ". " + panel_check_5.last_name
        
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

            panel_member_name_1 = panel_member_full_name_1,
            panel_member_name_2 = panel_member_full_name_2,
            panel_member_name_3 = panel_member_full_name_3,
            panel_member_name_4 = panel_member_full_name_4,
            panel_member_name_5 = panel_member_full_name_5,

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

            student_member_username_1 = student1_username_input,
            student_member_username_2 = student2_username_input,
            student_member_username_3 = student3_username_input,
            student_member_username_4 = student4_username_input,
            student_member_username_5 = student5_username_input,

            course = course_abbr,
            major = major_input,
            course_major_abbr = user_course,

            research_title = research_title_input.title(),

            date_submitted = date_today,

            form_status = "Pending"
            )

        panel_conforme_form.save()

        research_title_form = ResearchTitle(
            research_title =  research_title_input.title(),
            course_major_abbr = user_course,
            course = course_name,
            major = major_input,
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            status = "ongoing",
            date_submitted = date_today,
            )

        research_title_form.save()

        student_member_group_2 = StudentGroupMember(
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            student_member_username = student2_username_input,
            student_member_name = student2_input,
            course = course_name,
            major = major_input,
            course_major_abbr = user_course,
            )

        student_member_group_2.save()

        student_member_group_3 = StudentGroupMember(
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            student_member_username = student3_username_input,
            student_member_name = student3_input,
            course = course_name,
            major = major_input,
            course_major_abbr = user_course,
            )

        student_member_group_3.save()

        if student4_input:
            student_member_group_4 = StudentGroupMember(
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            student_member_username = student4_username_input,
            student_member_name = student4_input,
            course = course_name,
            major = major_input,
            course_major_abbr = user_course,
            )

            student_member_group_4.save()
        
        if student5_input:
            student_member_group_5 = StudentGroupMember(
            student_leader_username = current_user.username,
            student_leader_name = leader_member_name_2,
            student_member_username = student5_username_input,
            student_member_name = student5_input,
            course = course_name,
            major = major_input,
            course_major_abbr = user_course,
            )

            student_member_group_5.save()

        return redirect('student-dashboard')


    try:
        dept_head_check = User.objects.get(is_department_head=1)
        dept_head_name = None

        panel_check = User.objects.filter(is_panel=1)


        if dept_head_check.middle_name == "":
            dept_head_name = dept_head_check.honorific + " "  + dept_head_check.first_name + " " + dept_head_check.last_name
        
        else:
            dept_head_middle_initial = dept_head_check.middle_name[0]
            dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_middle_initial + ". " + dept_head_check.last_name


        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
            'currently_loggedin_user_account' : currently_loggedin_user_account,

            'dept_head_name': dept_head_name,

            'panel_members' : panel_members,

            'panel_check': panel_check,

            'leader_member_name' : leader_member_name_2,
            'leader_member_username' : current_user.username,


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
@user_passes_test(lambda u: u.is_student, login_url='index')
def studentPanelConformeBet3Form(request):
    current_user = (request.user)
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

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

        
        doc.save('2-PANEL-CONFROME-BET-3-{}.docx'.format(current_user))
        convert('2-PANEL-CONFROME-BET-3-{}.docx'.format(current_user))
        os.startfile('2-PANEL-CONFROME-BET-3-{}.pdf'.format(current_user))

        doc.save('2-PANEL-CONFORME-NEW.docx')
        convert("2-PANEL-CONFORME-NEW.docx")
        os.startfile('2-PANEL-CONFORME-NEW.pdf')

        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

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
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account': currently_loggedin_user_account
        }

    return render(request, 'admin-dashboard.html', context)


# Admin - Profile Page
@login_required(login_url='index')
def adminProfile(request):
    current_user = (request.user)
    current_password = (request.user.password)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Admin Profile
    current_username = (request.user.username)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_email = current_user.email


    context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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

        if current_password_input == current_password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    if request.method == "POST":
        course_input = request.POST.get('course_input')
        major_input = request.POST.get('major_input')
        course_abbr_input = request.POST.get('course_abbr_input')

        print(course_input)

        if StudentCourseMajor.objects.filter(major=major_input).exists():
            print("Major doesn't exist")

            context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
            'response': "major exist",
            }

            return render(request, 'admin-student-add-course-major.html', context)
            
        elif StudentCourseMajor.objects.filter(course_major_abbr=course_abbr_input).exists():
            print("Course Abbreviation doesn't exist")

            context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
            'currently_loggedin_user_account' : currently_loggedin_user_account,

            'response': "course abbr exist",
            }

            return render(request, 'admin-student-add-course-major.html', context)
            
        else:
            print("save")
            queryForm = StudentCourseMajor(course=course_input.title(), major=major_input.title(), course_major_abbr=course_abbr_input.upper())
            queryForm.save()

            context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
            'currently_loggedin_user_account' : currently_loggedin_user_account,
             
            'response': "added successfully",
            }

            return render(request, 'admin-student-add-course-major.html', context)

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
        'currently_loggedin_user_account' : currently_loggedin_user_account,
        }

    return render(request, 'admin-student-add-course-major.html', context)


# Admin - Department Head Account Page
@login_required(login_url='index')
def adminFacultyMemberAcc(request):
    current_user = (request.user)
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    user_middle_name = current_user.middle_name
    user_middle_initial = None

    members = User.objects.all().filter(is_faculty_member=1)

    # dept_head_check = User.objects.get(is_panel=1,)

    # print(dept_head_check.username)
    # dept_head_username = dept_head_check.username
    # dept_head_email = dept_head_check.email
    # dept_head_first_name = dept_head_check.first_name
    # dept_head_last_name = dept_head_check.last_name
    # dept_head_department = dept_head_check.department

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,
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
    current_password = current_user.password

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]


    form = SignUpForm()

    dit_head_exist = None

    try:
        User.objects.get(is_department_head=1)
        dit_head_exist = "exist"
    except:
        pass
    
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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                # Form
                'form': form,
                'dit_head_exist' : dit_head_exist,

                # Response
                'response' : "username or email exist",
            }

            return render(request, 'admin-faculty-member-create-acc.html', context)

    context = {
        # Topbar Start
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name, 
        'currently_loggedin_user_account' : currently_loggedin_user_account,

        # Form
        'form': form,

        'dit_head_exist' : dit_head_exist,
        }
    return render(request, 'admin-faculty-member-create-acc.html', context)


# Admin - Faculty Member Individual Account Page
@login_required(login_url='index')
def adminFacultyMemberData(request, id):
    current_user = (request.user)
    current_password = current_user.password

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

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
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

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

                sweet_member_check = User.objects.get(username=id)
                    
                sweet_member_username = sweet_member_check.username
                sweet_member_full_name = None

                if sweet_member_check.middle_name == "":
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                
                else:
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'members' : members,

                    'sweet_member_username' : sweet_member_username,
                    'sweet_member_full_name' : sweet_member_full_name,

                    'response' : "sweet profile updated"
                    }

                return render(request, 'admin-faculty-member-account.html', context)

            if member_check.username != username_input and member_check.email == email_input:
                try:
                    User.objects.get(username=username_input)

                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet partial update username exist"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.username=username_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=username_input)

                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

            if member_check.username == username_input and member_check.email != email_input:
                
                try:
                    User.objects.get(email=email_input)

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet partial update email exist"
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.email = email_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)
                
            if member_check.username != username_input and member_check.email != email_input:
                
                try:
                    User.objects.get(username=username_input)
                    User.objects.get(email=email_input)

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet partial update username and email exist"
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

                except:
                    member_check.username=username_input
                    member_check.email=email_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)
                
                    sweet_member_check = User.objects.get(username=username_input)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name
                
                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username' : sweet_member_username,
                        'sweet_member_full_name' : sweet_member_full_name,

                        'response' : "sweet profile updated"
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

        else:
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

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
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    faculty_member_check = User.objects.get(username=id)
    current_password = faculty_member_check.password

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == current_password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=faculty_member_check.username).update(password=new_password_input)

                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,

                        'response' : 'sweet password changed success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                else:
                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,

                        'response' : 'sweet confirm change password mismatch',
                    }

                    return render(request, 'admin-faculty-member-account.html', context)

            else:
                members = User.objects.all().filter(is_faculty_member=1)

                sweet_member_check = User.objects.get(username=id)
                    
                sweet_member_username = sweet_member_check.username
                sweet_member_full_name = None

                if sweet_member_check.middle_name == "":
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                
                else:
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'members' : members,

                    'sweet_member_username': sweet_member_username,
                    'sweet_member_full_name': sweet_member_full_name,

                    'response' : 'sweet same change password',
                }

                return render(request, 'admin-faculty-member-account.html', context)

        else:
            print("incorrect current password")
            members = User.objects.all().filter(is_faculty_member=1)

            sweet_member_check = User.objects.get(username=id)
                    
            sweet_member_username = sweet_member_check.username
            sweet_member_full_name = None

            if sweet_member_check.middle_name == "":
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
            
            else:
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'members' : members,

                'sweet_member_username': sweet_member_username,
                'sweet_member_full_name': sweet_member_full_name,

                'response' : 'sweet incorrect change current password',
                }

            return render(request, 'admin-faculty-member-account.html', context)

    return render(request, 'student-profile.html', context)


# Admin - Faculty Member Change User Account Process
@login_required(login_url='index')
def adminFacultyMemberChangeUserAccount(request, id):
    current_user = (request.user)
    current_password = current_user.password
    
    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

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
            
            sweet_member_check = User.objects.get(username=id)
                    
            sweet_member_username = sweet_member_check.username
            sweet_member_full_name = None

            if sweet_member_check.middle_name == "":
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
            
            else:
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'members' : members,

                'sweet_member_username': sweet_member_username,
                'sweet_member_full_name': sweet_member_full_name,

                'response' : "sweet choose user account"
                }

            return render(request, 'admin-faculty-member-account.html', context)

        if user_account_input not in user_account_list:
            print("User Account not in list")

            members = User.objects.all().filter(is_faculty_member=1)
            
            sweet_member_check = User.objects.get(username=id)
                    
            sweet_member_username = sweet_member_check.username
            sweet_member_full_name = None

            if sweet_member_check.middle_name == "":
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
            
            else:
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'members' : members,

                'sweet_member_username': sweet_member_username,
                'sweet_member_full_name': sweet_member_full_name,

                'response' : "sweet user account not in list"
                }

            return render(request, 'admin-faculty-member-account.html', context)

        if member_check.password == current_password_input:
            
            if member_check.department == user_account_input:

                members = User.objects.all().filter(is_faculty_member=1)

                sweet_member_check = User.objects.get(username=id)
                    
                sweet_member_username = sweet_member_check.username
                sweet_member_full_name = None
                sweet_member_department = sweet_member_check.department

                if sweet_member_check.middle_name == "":
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                
                else:
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                context = {
                    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                    'currently_loggedin_user_account' : currently_loggedin_user_account,

                    'members' : members,

                    'sweet_member_username': sweet_member_username,
                    'sweet_member_full_name': sweet_member_full_name,
                    'sweet_member_department': sweet_member_department,

                    'response' : 'sweet already',
                    }

                return render(request, 'admin-faculty-member-account.html', context)

            else:

                if user_account_input == "DIT Head":

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    sweet_member_check.department = user_account_input
                    sweet_member_check.is_department_head = 1
                    sweet_member_check.is_panel = 1
                    sweet_member_check.is_adviser = 1
                    sweet_member_check.is_subject_teacher = 1
                    sweet_member_check.is_academic_affairs = 0
                    sweet_member_check.is_library = 0
                    sweet_member_check.is_research_extension = 0
                    sweet_member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,
                        'sweet_member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Faculty Member":

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    sweet_member_check.department = user_account_input
                    sweet_member_check.is_department_head = 0
                    sweet_member_check.is_panel = 1
                    sweet_member_check.is_adviser = 1
                    sweet_member_check.is_subject_teacher = 1
                    sweet_member_check.is_academic_affairs = 0
                    sweet_member_check.is_library = 0
                    sweet_member_check.is_research_extension = 0
                    sweet_member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,
                        'sweet_member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Academic Affairs":

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    sweet_member_check.department = user_account_input
                    sweet_member_check.is_department_head = 0
                    sweet_member_check.is_panel = 0
                    sweet_member_check.is_adviser = 0
                    sweet_member_check.is_subject_teacher = 0
                    sweet_member_check.is_academic_affairs = 1
                    sweet_member_check.is_library = 0
                    sweet_member_check.is_research_extension = 0
                    sweet_member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,
                        'sweet_member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Library":

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    sweet_member_check.department = user_account_input
                    sweet_member_check.is_department_head = 0
                    sweet_member_check.is_panel = 0
                    sweet_member_check.is_adviser = 0
                    sweet_member_check.is_subject_teacher = 0
                    sweet_member_check.is_academic_affairs = 0
                    sweet_member_check.is_library = 1
                    sweet_member_check.is_research_extension = 0
                    sweet_member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,
                        'sweet_member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)

                if user_account_input == "Research & Extension":

                    sweet_member_check = User.objects.get(username=id)
                    
                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
                    
                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    sweet_member_check.department = user_account_input
                    sweet_member_check.is_department_head = 0
                    sweet_member_check.is_panel = 0
                    sweet_member_check.is_adviser = 0
                    sweet_member_check.is_subject_teacher = 0
                    sweet_member_check.is_academic_affairs = 0
                    sweet_member_check.is_library = 0
                    sweet_member_check.is_research_extension = 1
                    sweet_member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                        'currently_loggedin_user_account' : currently_loggedin_user_account,

                        'members' : members,

                        'sweet_member_username': sweet_member_username,
                        'sweet_member_full_name': sweet_member_full_name,
                        'sweet_member_department' : user_account_input,

                        'response' : 'sweet success',
                        }

                    return render(request, 'admin-faculty-member-account.html', context)
        
        else:
            members = User.objects.all().filter(is_faculty_member=1)

            sweet_member_check = User.objects.get(username=id)
                    
            sweet_member_username = sweet_member_check.username
            sweet_member_full_name = None

            if sweet_member_check.middle_name == "":
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name
            
            else:
                sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'currently_loggedin_user_account' : currently_loggedin_user_account,

                'members' : members,

                'sweet_member_username': sweet_member_username,
                'sweet_member_full_name': sweet_member_full_name,

                'response' : 'sweet incorrect current password',
                }

            return render(request, 'admin-faculty-member-account.html', context)



##########################################################################################################################

# DIT Head - Dashboard Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_department_head, login_url='index')
def ditHeadDashboard(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }

    return render(request, 'dit-head-dashboard.html', context)


# DIT Head - Profile Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_department_head, login_url='index')
def ditHeadProfile(request):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }
    

    context = {
                'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                'currently_loggedin_user_department' : currently_loggedin_user.department,
                'currently_loggedin_username':  currently_loggedin_user.username, 
                'currently_loggedin_user_email': currently_loggedin_user.email,
                }   

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == currently_loggedin_user.password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=currently_loggedin_user.username).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                        'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                        'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                        'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                        'currently_loggedin_user_department' : currently_loggedin_user.department,
                        'currently_loggedin_username':  currently_loggedin_user.username, 
                        'currently_loggedin_user_email': currently_loggedin_user.email,

                        "response": "new password and confirm new password doesnt match"
                        }

                    return render(request, 'dit-head-profile.html', context)

            else:
                context = {
                    'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                    'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                    'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                    'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                    'currently_loggedin_user_department' : currently_loggedin_user.department,
                    'currently_loggedin_username':  currently_loggedin_user.username, 
                    'currently_loggedin_user_email': currently_loggedin_user.email,

                    "response": "current password and new password is same"
                    }

                return render(request, 'dit-head-profile.html', context)

        else:
            context = {
                'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                'currently_loggedin_user_department' : currently_loggedin_user.department,
                'currently_loggedin_username':  currently_loggedin_user.username, 
                'currently_loggedin_user_email': currently_loggedin_user.email,

                "response": "current password is incorrect"
                }

            return render(request, 'dit-head-profile.html', context)


    return render(request, 'dit-head-profile.html', context)


# DIT Head - Panel Invitation  BET-3 Page
@login_required(login_url='index')
def ditHeadPanelInvitationBet3(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

     # PANEL INVITATION BET-3
    try:
        panel_invitation_bet3_check = PanelInvitation.objects.all().filter(dit_head_response="pending")
   
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            'panel_invitation_bet3_check' : panel_invitation_bet3_check,
            }

        return render(request, 'dit-head-panel-invitation-bet-3.html', context)

    except:
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }

        return render(request, 'dit-head-panel-invitation-bet-3.html', context)

# DIT Head - Panel Invitation BET-3 Accept Process
@login_required(login_url='index')
def ditHeadPanelInvitationBet3Accept(request, id):
    currently_loggedin_user = (request.user)
    
    print(id, type(id))

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        panel_invitation_bet3_check_form = PanelInvitation.objects.get(id = id)
   
        panel_invitation_bet3_check_form.dit_head_response = "accepted"
        panel_invitation_bet3_check_form.dit_head_response_date = dit_head_response_date

        panel_invitation_bet3_check_form.panel_member_response_1 = "pending"
        panel_invitation_bet3_check_form.panel_member_response_2 = "pending"
        panel_invitation_bet3_check_form.panel_member_response_3 = "pending"
        panel_invitation_bet3_check_form.panel_member_response_4 = "pending"
        panel_invitation_bet3_check_form.panel_member_response_5 = "pending"
        panel_invitation_bet3_check_form.save()

        panel_invitation_bet3_check = PanelInvitation.objects.all().filter(dit_head_response="pending")
   
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            'panel_invitation_bet3_check' : panel_invitation_bet3_check,

            'accepted_student_member_name' : panel_invitation_bet3_check_form.student_member_name_1,
            'accepted_student_member_username' : panel_invitation_bet3_check_form.student_member_username_1,

            'response' : 'sweet panel invitation bet-3 accepted',
            }

        return render(request, 'dit-head-panel-invitation-bet-3.html', context)

    except:
        print("NO FOUND")
        return redirect('dit-head-panel-invitation-bet-3')

# DIT Head - Panel Conforme BET-3 Page
@login_required(login_url='index')
def ditHeadPanelConformeBet3(request):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

     # PANEL CONFORME BET-3
    try:
        panel_conforme_bet3_check = PanelConformeBET3.objects.all().filter(dept_head_status="pending")
   
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            'panel_conforme_bet3_check' : panel_conforme_bet3_check,
            }

        return render(request, 'dit-head-panel-conforme-bet-3.html', context)

    except:
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }

        return render(request, 'dit-head-panel-conforme-bet-3.html', context)

# DIT Head - Panel Conforme BET-3 Accept Process
@login_required(login_url='index')
def ditHeadPanelConformeBet3Accept(request, id):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name
    
    # PANEL CONFORME BET-3
    try:
        panel_conforme_bet3_check_form = PanelConformeBET3.objects.get(id=id)
        
        panel_conforme_bet3_check_form.dept_head_status = "accepted"
        panel_conforme_bet3_check_form.panel_member_status_1 = "pending"
        panel_conforme_bet3_check_form.panel_member_status_2 = "pending"
        panel_conforme_bet3_check_form.panel_member_status_3 = "pending"
        panel_conforme_bet3_check_form.panel_member_status_4 = "pending"
        panel_conforme_bet3_check_form.panel_member_status_5 = "pending"
        panel_conforme_bet3_check_form.save()


        panel_conforme_bet3_check = PanelConformeBET3.objects.all().filter(dept_head_status="pending")
   
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            'panel_conforme_bet3_check' : panel_conforme_bet3_check,

            'accepted_research_title' : panel_conforme_bet3_check_form.research_title,

            'response' : 'sweet panel conforme bet-3 accepted',
            }

        return render(request, 'dit-head-panel-conforme-bet-3.html', context)

    except:
        return redirect('dit-head-panel-conforme-bet-3.html')

# DIT Head - Panel Conforme BET-3 Decline Process
@login_required(login_url='index')
def ditHeadPanelConformeBet3Decline(request, id):
    pass

##########################################################################################################################

# Panel - Dashboard Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_panel, login_url='index')
def panelDashboard(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    
    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }

    return render(request, 'panel-dashboard.html', context)


# Panel - Profile Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_panel, login_url='index')
def panelProfile(request):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }
    

    context = {
                'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                'currently_loggedin_user_department' : currently_loggedin_user.department,
                'currently_loggedin_username':  currently_loggedin_user.username, 
                'currently_loggedin_user_email': currently_loggedin_user.email,
                }   

    if request.method == 'POST':
        current_password_input = request.POST.get('current_password_input')
        new_password_input = request.POST.get('new_password_input')
        confirm_new_password_input = request.POST.get('confirm_new_password_input')

        if current_password_input == currently_loggedin_user.password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=currently_loggedin_user.username).update(password=new_password_input)

                    context = {                        
                        "response": "changed password"
                        }
                    return render(request, 'index.html', context)

                else:
                    context = {
                        'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                        'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                        'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                        'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                        'currently_loggedin_user_department' : currently_loggedin_user.department,
                        'currently_loggedin_username':  currently_loggedin_user.username, 
                        'currently_loggedin_user_email': currently_loggedin_user.email,

                        "response": "new password and confirm new password doesnt match"
                        }

                    return render(request, 'panel-profile.html', context)

            else:
                context = {
                    'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                    'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                    'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                    'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                    'currently_loggedin_user_department' : currently_loggedin_user.department,
                    'currently_loggedin_username':  currently_loggedin_user.username, 
                    'currently_loggedin_user_email': currently_loggedin_user.email,

                    "response": "current password and new password is same"
                    }

                return render(request, 'panel-profile.html', context)

        else:
            context = {
                'currently_loggedin_user_full_name' : currently_loggedin_user_full_name,

                'currently_loggedin_user_first_name': currently_loggedin_user.first_name,
                'currently_loggedin_user_middle_name' : currently_loggedin_user.middle_name,
                'currently_loggedin_user_last_name' : currently_loggedin_user.last_name,
                'currently_loggedin_user_department' : currently_loggedin_user.department,
                'currently_loggedin_username':  currently_loggedin_user.username, 
                'currently_loggedin_user_email': currently_loggedin_user.email,

                "response": "current password is incorrect"
                }

            return render(request, 'panel-profile.html', context)


    return render(request, 'panel-profile.html', context)


# Panel - Panel Invitation  BET-3 Page
@login_required(login_url='index')
def panelPanelInvitationBet3(request):
    currently_loggedin_user = (request.user)
    print("Current User:", currently_loggedin_user.username)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # PANEL INVITATION BET-3
    panel_invitation_bet3_check_1 = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
    panel_invitation_bet3_check_2 = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
    panel_invitation_bet3_check_3 = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
    panel_invitation_bet3_check_4 = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
    panel_invitation_bet3_check_5 = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")
    
    print(panel_invitation_bet3_check_1)
    print(panel_invitation_bet3_check_2)
    print(panel_invitation_bet3_check_3)
    print(panel_invitation_bet3_check_4)
    print(panel_invitation_bet3_check_5)

    context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1,
            "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2,
            "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3,
            "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4,
            "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5,
            
            }

    return render(request, 'panel-panel-invitation-bet-3.html', context)

# Panel - Panel Invitation BET-3 Accept Process
@login_required(login_url='index')
def panelPanelInvitationBet3Accept(request, id):
    currently_loggedin_user = (request.user)
    
    print(id, type(id))

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        panel_invitation_bet3_check_1 = PanelInvitation.objects.get(id = id, panel_member_username_1 = currently_loggedin_user.username)
   
        panel_invitation_bet3_check_1.panel_member_response_1 = "accepted"
        panel_invitation_bet3_check_1.panel_member_response_date_1 = response_date

        panel_invitation_bet3_check_1.save()

        panel_invitation_bet_3_check_all = PanelInvitation.objects.get(id = id)

        if panel_invitation_bet_3_check_all.panel_member_response_1 == "accepted" and \
                panel_invitation_bet_3_check_all.panel_member_response_2 == "accepted" and \
                    panel_invitation_bet_3_check_all.panel_member_response_3 == "accepted" and \
                        panel_invitation_bet_3_check_all.panel_member_response_4 == "accepted" and \
                            panel_invitation_bet_3_check_all.panel_member_response_5 == "accepted":

            panel_invitation_bet_3_check_all.form_status = "Complete"
            panel_invitation_bet_3_check_all.save() 
            

        panel_invitation_bet3_check_1_new = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
        panel_invitation_bet3_check_2_new = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
        panel_invitation_bet3_check_3_new = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
        panel_invitation_bet3_check_4_new = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
        panel_invitation_bet3_check_5_new = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

        context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

                "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1_new,
                "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2_new,
                "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3_new,
                "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4_new,
                "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5_new,

                'accepted_student_member_name' : panel_invitation_bet_3_check_all.student_member_name_1,
                'accepted_student_member_username' : panel_invitation_bet_3_check_all.student_member_username_1,

                'response' : 'sweet panel invitation bet-3 accepted',
                
                }
        print("pass all")
        return render(request, 'panel-panel-invitation-bet-3.html', context)
        
    except:
        pass
    
    try:
        panel_invitation_bet3_check_2 = PanelInvitation.objects.get(id = id, panel_member_username_2 = currently_loggedin_user.username)
   
        panel_invitation_bet3_check_2.panel_member_response_2 = "accepted"
        panel_invitation_bet3_check_2.panel_member_response_date_2 = response_date

        panel_invitation_bet3_check_2.save()

        panel_invitation_bet_3_check_all = PanelInvitation.objects.get(id = id)

        if panel_invitation_bet_3_check_all.panel_member_response_1 == "accepted" and \
                panel_invitation_bet_3_check_all.panel_member_response_2 == "accepted" and \
                    panel_invitation_bet_3_check_all.panel_member_response_3 == "accepted" and \
                        panel_invitation_bet_3_check_all.panel_member_response_4 == "accepted" and \
                            panel_invitation_bet_3_check_all.panel_member_response_5 == "accepted":

            panel_invitation_bet_3_check_all.form_status = "Complete"
            panel_invitation_bet_3_check_all.save() 


        panel_invitation_bet3_check_1_new = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
        panel_invitation_bet3_check_2_new = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
        panel_invitation_bet3_check_3_new = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
        panel_invitation_bet3_check_4_new = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
        panel_invitation_bet3_check_5_new = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

        context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

                "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1_new,
                "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2_new,
                "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3_new,
                "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4_new,
                "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5_new,

                'accepted_student_member_name' : panel_invitation_bet_3_check_all.student_member_name_1,
                'accepted_student_member_username' : panel_invitation_bet_3_check_all.student_member_username_1,

                'response' : 'sweet panel invitation bet-3 accepted',
                
                }
        print("pass all")
        return render(request, 'panel-panel-invitation-bet-3.html', context)
        
    except:
        pass

    try:
        panel_invitation_bet3_check_3 = PanelInvitation.objects.get(id = id, panel_member_username_3 = currently_loggedin_user.username)
   
        panel_invitation_bet3_check_3.panel_member_response_3 = "accepted"
        panel_invitation_bet3_check_3.panel_member_response_date_3 = response_date

        panel_invitation_bet3_check_3.save()

        panel_invitation_bet_3_check_all = PanelInvitation.objects.get(id = id)
        
        if panel_invitation_bet_3_check_all.panel_member_response_1 == "accepted" and \
                panel_invitation_bet_3_check_all.panel_member_response_2 == "accepted" and \
                    panel_invitation_bet_3_check_all.panel_member_response_3 == "accepted" and \
                        panel_invitation_bet_3_check_all.panel_member_response_4 == "accepted" and \
                            panel_invitation_bet_3_check_all.panel_member_response_5 == "accepted":

            panel_invitation_bet_3_check_all.form_status = "Complete"
            panel_invitation_bet_3_check_all.save() 


        panel_invitation_bet3_check_1_new = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
        panel_invitation_bet3_check_2_new = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
        panel_invitation_bet3_check_3_new = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
        panel_invitation_bet3_check_4_new = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
        panel_invitation_bet3_check_5_new = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

        context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

                "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1_new,
                "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2_new,
                "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3_new,
                "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4_new,
                "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5_new,

                'accepted_student_member_name' : panel_invitation_bet_3_check_all.student_member_name_1,
                'accepted_student_member_username' : panel_invitation_bet_3_check_all.student_member_username_1,

                'response' : 'sweet panel invitation bet-3 accepted',
                
                }
        print("pass all")
        return render(request, 'panel-panel-invitation-bet-3.html', context)
        
    except:
        pass

    try:
        panel_invitation_bet3_check_4 = PanelInvitation.objects.get(id = id, panel_member_username_4 = currently_loggedin_user.username)
   
        panel_invitation_bet3_check_4.panel_member_response_4 = "accepted"
        panel_invitation_bet3_check_4.panel_member_response_date_4 = response_date

        panel_invitation_bet3_check_4.save()

        panel_invitation_bet_3_check_all = PanelInvitation.objects.get(id = id)
        
        if panel_invitation_bet_3_check_all.panel_member_response_1 == "accepted" and \
                panel_invitation_bet_3_check_all.panel_member_response_2 == "accepted" and \
                    panel_invitation_bet_3_check_all.panel_member_response_3 == "accepted" and \
                        panel_invitation_bet_3_check_all.panel_member_response_4 == "accepted" and \
                            panel_invitation_bet_3_check_all.panel_member_response_5 == "accepted":

            panel_invitation_bet_3_check_all.form_status = "Complete"
            panel_invitation_bet_3_check_all.save() 


        panel_invitation_bet3_check_1_new = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
        panel_invitation_bet3_check_2_new = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
        panel_invitation_bet3_check_3_new = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
        panel_invitation_bet3_check_4_new = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
        panel_invitation_bet3_check_5_new = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

        context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

                "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1_new,
                "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2_new,
                "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3_new,
                "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4_new,
                "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5_new,

                'accepted_student_member_name' : panel_invitation_bet_3_check_all.student_member_name_1,
                'accepted_student_member_username' : panel_invitation_bet_3_check_all.student_member_username_1,

                'response' : 'sweet panel invitation bet-3 accepted',
                
                }
        print("pass all")
        return render(request, 'panel-panel-invitation-bet-3.html', context)
        
    except:
        pass

    try:
        panel_invitation_bet3_check_5 = PanelInvitation.objects.get(id = id, panel_member_username_5 = currently_loggedin_user.username)
   
        panel_invitation_bet3_check_5.panel_member_response_5 = "accepted"
        panel_invitation_bet3_check_5.panel_member_response_date_5 = response_date

        panel_invitation_bet3_check_5.save()

        panel_invitation_bet_3_check_all = PanelInvitation.objects.get(id = id)
        
        if panel_invitation_bet_3_check_all.panel_member_response_1 == "accepted" and \
                panel_invitation_bet_3_check_all.panel_member_response_2 == "accepted" and \
                    panel_invitation_bet_3_check_all.panel_member_response_3 == "accepted" and \
                        panel_invitation_bet_3_check_all.panel_member_response_4 == "accepted" and \
                            panel_invitation_bet_3_check_all.panel_member_response_5 == "accepted":

            panel_invitation_bet_3_check_all.form_status = "Complete"
            panel_invitation_bet_3_check_all.save() 


        panel_invitation_bet3_check_1_new = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
        panel_invitation_bet3_check_2_new = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
        panel_invitation_bet3_check_3_new = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
        panel_invitation_bet3_check_4_new = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
        panel_invitation_bet3_check_5_new = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

        context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

                "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1_new,
                "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2_new,
                "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3_new,
                "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4_new,
                "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5_new,

                'accepted_student_member_name' : panel_invitation_bet_3_check_all.student_member_name_1,
                'accepted_student_member_username' : panel_invitation_bet_3_check_all.student_member_username_1,

                'response' : 'sweet panel invitation bet-3 accepted',
                
                }
        print("pass all")
        return render(request, 'panel-panel-invitation-bet-3.html', context)
        
    except:
        pass

    print("PASS ALL")
    panel_invitation_bet3_check_1 = PanelInvitation.objects.all().filter(panel_member_username_1 = currently_loggedin_user.username, panel_member_response_1 = "pending")
    panel_invitation_bet3_check_2 = PanelInvitation.objects.all().filter(panel_member_username_2 = currently_loggedin_user.username, panel_member_response_2 = "pending")
    panel_invitation_bet3_check_3 = PanelInvitation.objects.all().filter(panel_member_username_3 = currently_loggedin_user.username, panel_member_response_3 = "pending")
    panel_invitation_bet3_check_4 = PanelInvitation.objects.all().filter(panel_member_username_4 = currently_loggedin_user.username, panel_member_response_4 = "pending")
    panel_invitation_bet3_check_5 = PanelInvitation.objects.all().filter(panel_member_username_5 = currently_loggedin_user.username, panel_member_response_5 = "pending")

    context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            "panel_invitation_bet3_check_1": panel_invitation_bet3_check_1,
            "panel_invitation_bet3_check_2": panel_invitation_bet3_check_2,
            "panel_invitation_bet3_check_3": panel_invitation_bet3_check_3,
            "panel_invitation_bet3_check_4": panel_invitation_bet3_check_4,
            "panel_invitation_bet3_check_5": panel_invitation_bet3_check_5,
            
            }

    return render(request, 'panel-panel-invitation-bet-3.html', context)



# Panel - Panel Conforme BET-3 Page
@login_required(login_url='index')
def panelPanelConformeBet3(request):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

     # PANEL CONFORME BET-3
    try:
        panel_conforme_bet3_check_1 = PanelConformeBET3.objects.all().filter(panel_member_1 = currently_loggedin_user.username, panel_member_status_1="pending")
    except:
        print("Not Panel 1")
        pass

    try:
        panel_conforme_bet3_check_2 = PanelConformeBET3.objects.all().filter(panel_member_2 = currently_loggedin_user.username, panel_member_status_2="pending")
    except:
        print("Not Panel 2")
        pass

    try:
        panel_conforme_bet3_check_3 = PanelConformeBET3.objects.all().filter(panel_member_3 = currently_loggedin_user.username, panel_member_status_3="pending")
    except:
        print("Not Panel 3")
        pass

    try:
        panel_conforme_bet3_check_4 = PanelConformeBET3.objects.all().filter(panel_member_4 = currently_loggedin_user.username, panel_member_status_4="pending")
    except:
        print("Not Panel 4")
        pass

    try:
        panel_conforme_bet3_check_5 = PanelConformeBET3.objects.all().filter(panel_member_5 = currently_loggedin_user.username, panel_member_status_5="pending")
    except:
        print("Not Panel 5")
        pass


    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

        'panel_conforme_bet3_check_1' : panel_conforme_bet3_check_1,
        'panel_conforme_bet3_check_2' : panel_conforme_bet3_check_2,
        'panel_conforme_bet3_check_3' : panel_conforme_bet3_check_3,
        'panel_conforme_bet3_check_4' : panel_conforme_bet3_check_4,
        'panel_conforme_bet3_check_5' : panel_conforme_bet3_check_5,
        }

    return render(request, 'panel-panel-conforme-bet-3.html', context)

# Panel - Panel Conforme BET-3 Accept Process
@login_required(login_url='index')
def panelPanelConformeBet3Accept(request, id):
    currently_loggedin_user = (request.user)

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name
    
    # PANEL CONFORME BET-3
    try:
        panel_conforme_bet3_check_form = PanelConformeBET3.objects.get(id=id)

        if panel_conforme_bet3_check.panel_member_1 == currently_loggedin_user.username:
            panel_conforme_bet3_check_form.panel_member_status_1 = "accepted"
            panel_conforme_bet3_check_form.save()
        
        elif panel_conforme_bet3_check.panel_member_2 == currently_loggedin_user.username:
            panel_conforme_bet3_check_form.panel_member_status_2 = "accepted"
            panel_conforme_bet3_check_form.save()
        
        elif panel_conforme_bet3_check.panel_member_3 == currently_loggedin_user.username:
            panel_conforme_bet3_check_form.panel_member_status_3 = "accepted"
            panel_conforme_bet3_check_form.save()

        elif panel_conforme_bet3_check.panel_member_4 == currently_loggedin_user.username:
            panel_conforme_bet3_check_form.panel_member_status_4 = "accepted"
            panel_conforme_bet3_check_form.save()

        elif panel_conforme_bet3_check.panel_member_5 == currently_loggedin_user.username:
            panel_conforme_bet3_check_form.panel_member_status_5 = "accepted"
            panel_conforme_bet3_check_form.save()


        panel_conforme_bet3_check = PanelConformeBET3.objects.all().filter(dept_head_status="pending")
   
        context = {
            'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

            'panel_conforme_bet3_check' : panel_conforme_bet3_check,

            'accepted_research_title' : panel_conforme_bet3_check_form.research_title,

            'response' : 'sweet panel conforme bet-3 accepted',
            }

        return render(request, 'panel-panel-conforme-bet-3.html', context)

    except:
        return redirect('panel-panel-conforme-bet-3.html')


##########################################################################################################################

# Subject Teacher - Dashboard Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_subject_teacher, login_url='index')
def subjectTeacherDashboard(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    
    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        }

    return render(request, 'subject-teacher-dashboard.html', context)

# Subject Teacher - Research Title Defense Dashboard Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_subject_teacher, login_url='index')
def subjectTeacherResearchTitleDefenseDashboard(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username = currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)
    
    if request.method == 'POST':
        course_input = request.POST.get('course_input')
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username = currently_loggedin_user.username, course = course_input)
            student_defense_unscheduled = StudentLeader.objects.all().filter(bet3_subject_teacher_username = currently_loggedin_user.username, course_major_abbr = course_input, defense_status = "")
            
            print(student_defense_unscheduled)
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'course_handled_list': course_handled_list,

                'student_defense_scheduled' : student_defense_scheduled,
                'student_defense_unscheduled' : student_defense_unscheduled,
                }

            return render(request, 'subject-teacher-research-title-defense-dashboard.html', context)

        except:
            pass
    
    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'course_handled_list': course_handled_list,
        }

    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,

        'course_handled_list': course_handled_list,
        }

    return render(request, 'subject-teacher-research-title-defense-dashboard.html', context)

# Subject Teacher - Set Research Title Defense Schedule Page
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_subject_teacher, login_url='index')
def subjectTeacherSetResearchTitleDefenseSchedule(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username = currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == 'POST':
        course_input = request.POST.get('course_input')
        print(course_input)

        try:
            course_defense_schedules = DefenseSchedule.objects.all().filter(username = currently_loggedin_user.username, course = course_input)
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'course_handled_list': course_handled_list,

                'course_defense_schedules' : course_defense_schedules,
                }

            return render(request, 'subject-teacher-set-research-title-defense.html', context)

        except:
            pass
    
    context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'course_handled_list': course_handled_list,
        }

    return render(request, 'subject-teacher-set-research-title-defense.html', context)

# Subject Teacher - Save Research Title Defense Schedule Process
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_subject_teacher, login_url='index')
def subjectTeacherSaveResearchTitleDefenseSchedule(request):
    currently_loggedin_user = (request.user)

    topbar_data = topbarProcess(request);
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []
    defense_time_list = ['8:00 AM-9:00 AM', '9:00 AM-10:00 AM', '10:00 AM-11:00 AM', '1:00 PM-2:00 PM', '2:00 PM-3:00 PM', '3:00 PM-4:00 PM', '4:00 PM-5:00 PM']

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username = currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))    

    if request.method == 'POST':
        course_input = request.POST.get('course_input')
        date_input = request.POST.get('date_input')
        time_input = request.POST.get('time_input')

        if course_input not in course_handled_list:
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'course_handled_list' : course_handled_list,
                'response' : 'sweet invalid course'
                }

            return render(request, 'subject-teacher-set-research-title-defense.html', context)

        if time_input not in defense_time_list:

            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'course_handled_list' : course_handled_list,
                'response' : 'sweet invalid defense time'
                }

            return render(request, 'subject-teacher-set-research-title-defense.html', context)

        js_month = date_input.split("-")[1]
        js_date = date_input.split("-")[2]
        js_year = date_input.split("-")[0]

        start_time = time_input.split("-")[0]
        end_time = time_input.split("-")[1]

        py_date = date(day= int(js_date), month=int(js_month), year=int(js_year)).strftime('%B %d, %Y')

        print(course_input)
        print(py_date)
        print(start_time)
        print(end_time)

        try:
            DefenseSchedule.objects.get(username = currently_loggedin_user.username, course = course_input, form = 'Research Title Defense', date = py_date, start_time = start_time, end_time = end_time)
        
            context = {
                'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
                'course_handled_list' : course_handled_list,
                'response' : 'scheduled date exist'
                }

            return render(request, 'subject-teacher-set-research-title-defense.html', context)

        except:
            print("do not exist")
            pass

        defense_schedule = DefenseSchedule(
            username = currently_loggedin_user.username,
            name = currently_loggedin_user_full_name,
            course = course_input,
            form = "Research Title Defense",
            date = py_date,
            start_time = start_time,
            end_time = end_time,
            status = "Available"
        )
        defense_schedule.save()

        context = {
        'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
        'course_handled_list' : course_handled_list,

        'response' : 'schedule saved'
        }

        return render(request, 'subject-teacher-set-research-title-defense.html', context)



    context = {
    'currently_loggedin_user_full_name': currently_loggedin_user_full_name,
    'course_handled_list' : course_handled_list,
    }

    return render(request, 'subject-teacher-set-research-title-defense.html', context)

# Subject Teacher - Delete Research Title Defense Schedule Process
@login_required(login_url='index')
@user_passes_test(lambda u: u.is_subject_teacher, login_url='index')
def subjectTeacherDeleteResearchTitleDefenseSchedule(request, id):
    currently_loggedin_user = (request.user)

    delete_date = DefenseSchedule.objects.filter(username=currently_loggedin_user.username, id=id, status = "Available")
    print(delete_date)

    if not delete_date:
            context = {
            'response' : 'sweet schedule not found'
            }
            
            return render(request, 'subject-teacher-set-research-title-defense.html', context)
        
    else:
        delete_date.delete()

        context = {
                'response' : 'schedule deleted'
                }

        return render(request, 'subject-teacher-set-research-title-defense.html', context)

@login_required(login_url='index')
def topbarProcess(request):

    currently_loggedin_user = (request.user)
    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None
    currently_loggedin_user_account = None

    if currently_loggedin_user_middle_name == "":
       currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    if currently_loggedin_user.is_student == 1:
        currently_loggedin_user_account = 'Student'
    
    elif currently_loggedin_user.is_administrator == 1:
        currently_loggedin_user_account = 'Administrator'
    
    elif currently_loggedin_user.is_academic_affairs == 1:
        currently_loggedin_user_account = 'Academic Affairs'
    
    elif currently_loggedin_user.is_library == 1:
        currently_loggedin_user_account = 'Library'

    elif currently_loggedin_user.is_research_extension == 1:
        currently_loggedin_user_account = 'Research & Extension'

    return (currently_loggedin_user_full_name, currently_loggedin_user_account)