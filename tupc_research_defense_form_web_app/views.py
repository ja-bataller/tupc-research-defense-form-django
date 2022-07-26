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


# Student - Panel Conforme BET-3 Process
@login_required(login_url='index')
def studentPanelConformeBet3(request):
    current_user = (request.user)

    try:
        panel_conforme_bet3_check = PanelConformeBET3.objects.get(student_leader_username=current_user)
        print("Panel Conforme - BET-3 Exist")
        return redirect('student-panel-conforme-bet3-form')

    except:
        print("Panel Conforme - BET-3 Create")
        return redirect('student-panel-conforme-bet3-create')

##################################################################################

# Student - Panel Conforme BET-3 Create Page
@login_required(login_url='index')
def studentPanelConformeBet3Create(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_full_name = user_first_name + " " + user_last_name

    user_middle_initial = None
    leader_member_name = None
    leader_member_name_2 = None

    user_course = current_user.course
    
    if user_middle_name == "":
        leader_member_name = user_first_name + " " + user_last_name
        leader_member_name_2 = user_last_name + ", " + user_first_name

    else:
        user_middle_initial = user_middle_name[0]
        leader_member_name = user_first_name + " " + user_middle_initial + ". " + user_last_name
        leader_member_name_2 = user_last_name + ", " + user_first_name + " " + user_middle_initial + "."

    if request.method == "POST":
        # Textual month, day and year	
        date_today = today.strftime("%B %d, %Y")
        print("Date Submitted =", date_today)

        dept_head_check = User.objects.get(is_department_head=1)

        dept_head_name_input = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name
        print("Department Head =", dept_head_name_input)


        panel1_input = request.POST.get('panel1_input')
        print("Panel 1 =", panel1_input)

        panel2_input = request.POST.get('panel2_input')
        print("Panel 2 =", panel2_input)

        panel3_input = request.POST.get('panel3_input')
        print("Panel 3 =", panel3_input)

        panel4_input = request.POST.get('panel4_input')
        print("Panel 4 =", panel4_input)

        panel5_input = request.POST.get('panel5_input')
        print("Panel 5 =", panel5_input)

        student1_input = leader_member_name_2
        print("Student 1 =", student1_input)

        student2_input = request.POST.get('student2_input')
        print("Student 2 =", student2_input)

        student3_input = request.POST.get('student3_input')
        print("Student 3 =", student3_input)

        student4_input = request.POST.get('student4_input')
        print("Student 4 =", student4_input)

        student5_input = request.POST.get('student5_input')
        print("Student 5 =", student5_input)


        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        course_input = course_name
        course_abbr = course_input.replace("Engineering", "Eng.")
        print("Course =", course_abbr)

        major_input = major_name
        print("Major =", major_input)

        research_title_input = request.POST.get('research_title_input')
        print("Research Title =", research_title_input)

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

            research_title = research_title_input,

            date_submitted = date_today,

            form_status = "Pending"
            )

        panel_conforme_form.save()
        return redirect('student-dashboard')


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
##################################################################################


# Student - Panel Conforme BET-3 Form Page
@login_required(login_url='index')
def studentPanelConformeBet3Form(request):
    current_user = (request.user)
    currentpassword = (request.user.password)

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_full_name = user_first_name + " " + user_last_name


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

    form_status = panel_conforme_bet3_check.form_status

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

        panel_member = adviser_table.cell(0, 0).paragraphs[0].runs[0].text = 'Mr. Jay Victor Gumboc'
        date_signed = adviser_table.cell(0, 2).paragraphs[0].runs[0].text = 'July 8, 2022'

        print(doc.paragraphs[1].runs[1].text) # Date Today 1
        print(doc.paragraphs[3].runs[0].text) # Receiver 1
        print(doc.paragraphs[6].runs[1].text) # Receiver 2
        print(doc.paragraphs[7].runs[1].text) # Subject
        print(doc.paragraphs[7].runs[4].text) # Student Course
        print(doc.paragraphs[7].runs[6].text) # Student Major
        print(doc.paragraphs[10].runs[1].text) # Research Title
        print(doc.paragraphs[15].runs[0].text) # Department Head Name

        doc.paragraphs[1].runs[1].text = 'July 8, 2022'
        doc.paragraphs[3].runs[0].text = 'Mr. Jay Victor Gumboc'
        doc.paragraphs[6].runs[1].text = 'Mr. Jay Victor Gumboc'
        doc.paragraphs[7].runs[1].text = 'BET-3'
        doc.paragraphs[7].runs[4].text = 'Bachelor of Engineering Technology'
        doc.paragraphs[7].runs[6].text = 'Major in Computer Engienering Technology'
        doc.paragraphs[10].runs[1].text = 'Development of Research Defense Form Web Application'
        doc.paragraphs[15].runs[0].text = 'Mr. Jay Victor Gumboc'

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
                user_check.honorific = request.POST.get('honorific_input')
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
                user_check.honorific = request.POST.get('honorific_input')
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