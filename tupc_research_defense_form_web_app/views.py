from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.conf import settings

from .forms import *
from .models import *

# Import Date & Time
from datetime import date
import time

# Import Docx and PDF Convert
from docx import Document
from docx2pdf import convert
from docx.shared import Inches
import qrcode
import os
import subprocess
import base64
from django.core.files.storage import FileSystemStorage
import cv2

from .students_views import *
from .admin_views import *
from .dit_head_views import *
from .panel_views import *
from .subject_teacher_views import *
from .adviser_views import *
from .research_ext_views import *
from.adaa_views import *
from.library_views import *
from .students_download_views import *

import string    
import random

# Set Timezone to Manila
# os.environ["TZ"] = "Asia/Manila"
# time.tzset()


today = date.today()
date_today = today.strftime("%B %d, %Y")

##########################################################################################################################

# Index / Log in Page
def index(request):
    return render(request, "index.html")


# Index / Log in Page
def loginPage(request):

    if request.method == "POST":
        # Get data from Front-end
        username_input_index_form = request.POST.get("username_input")
        password_input_index_form = request.POST.get("password_input")

        # Check if the user exist
        try:
            user_check = User.objects.get(username=username_input_index_form)

            # Check the password of the user if correct
            if user_check.password == password_input_index_form:
                print("The Password is correct")

                if user_check.is_student == 1:
                    print("User: Student")
                    # Get All Course
                    course = StudentCourseMajor.objects.all()
                    course_list = []

                    # Check if there is DIT Head assigned
                    try:
                        # Get DIT Head
                        get_department_head = User.objects.get(is_department_head=1)
                    except:
                        print("No DIT Head assigned")

                        context = {
                            "response": "sweet no dit head assigned"}

                        return render(request, "signup.html", context)

                    

                    # Get All Panel
                    panel_members = User.objects.all().filter(is_panel=1)

                    # Get All Adviser
                    adviser = User.objects.all().filter(is_adviser=1)

                    # Get All Subject Teachers
                    subject_teachers = User.objects.all().filter(is_subject_teacher=1)
                    subject_teacher_list = []

                    # Get All Academic Affairs
                    academic_affairs = User.objects.all().filter(is_academic_affairs=1)

                    # Get All Library
                    library = User.objects.all().filter(is_library=1)

                    # Get All Research & Extension
                    research_extension = User.objects.all().filter(is_research_extension=1)

                    print(panel_members.count())

                    # Check if there are no available course
                    if not course:
                        print("No Course Available")

                        context = {
                            "response": "sweet no course available"}

                        return render(request, "login.html", context)

                    else:
                        for course_abbr in course:
                            course_list.append(course_abbr.course_major_abbr)

                    # Check if there are no Panel Members assigned
                    if not panel_members:
                        print("No Panel assigned")

                        context = {
                            "response": "sweet no panel assigned"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    # Check if Panel Members is incomplete
                    if panel_members.count() < 6:
                        print("Incomplete Panel Members")

                        context = {
                            "response": "sweet incomplete panel"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    # Check if there are no subject teacher assigned
                    if not subject_teachers:
                        print("No Subject Teachers assigned")

                        context = {"response": "sweet no subject teacher assigned"
                            }

                        return render(request, "login.html", context)

                    else:
                        for subject_teacher in subject_teachers:

                            subject_teacher_full_name = None

                            if subject_teacher.middle_name == "":
                                subject_teacher_full_name = subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.last_name + " " + subject_teacher.suffix
                                subject_teacher_list.append(subject_teacher_full_name)
                            else:
                                subject_teacher_full_name = subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.middle_name[0] + ". " + subject_teacher.last_name + " " + subject_teacher.suffix
                                subject_teacher_list.append(subject_teacher_full_name)

                        print("Available Course: ", course_list)
                        print("Available Subject Teachers: ", subject_teacher_list)

                        subject_teacher_list.sort()


                    # Check if there are no Adviser assigned
                    if not adviser:
                        print("No Adviser assigned")

                        context = {
                            "response": "sweet no adviser assigned"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    # Check if there are no Academic Affairs assigned
                    if not academic_affairs:
                        print("No Academic Affairs assigned")

                        context = {
                            "response": "sweet no academic affairs assigned"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    # Check if there are no Library assigned
                    if not library:
                        print("No Library assigned")

                        context = {
                            "response": "sweet no library assigned"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    # Check if there are no Research & Extension assigned
                    if not research_extension:
                        print("No Research & Extension assigned")

                        context = {
                            "response": "sweet no research extension assigned"}

                        return render(request, "login.html", context)

                    else:
                        pass

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("student-dashboard")

                if user_check.is_administrator == 1:
                    print("User: Admin")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("admin-dashboard")

                if user_check.is_department_head == 1:
                    print("User: DIT Head")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("login-as")

                if user_check.is_panel == 1:
                    print("User: Panel")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("login-as")
                
                if user_check.is_academic_affairs == True:
                    print("User: Academic Affairs Office")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("academic-affairs-office-dashboard")
                
                if user_check.is_library == True:
                    print("User: Libary")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("library-dashboard")
                
                if user_check.is_research_extension == True:
                    print("User: Research & Extension")

                    user = User.objects.get(username=username_input_index_form, password=password_input_index_form)
                    login(request, user)

                    return redirect("research-extension-dashboard")

            else:
                print("The Password is incorrect.")

                context = {"response": "incorrect password"}
                return render(request, "login.html", context)

        # If the user doesn't exist
        except:
            print("The User doesn't exist.")

            context = {"response": "user does not exist"}
            return render(request, "index.html", context)

    return render(request, "login.html")


#  Sign up Page
def signup(request):

    form = SignUpForm()

    suffix_list = ["", "Sr.", "Jr.", "I", "II", "III", "IV", "V"]

    # Get All Course
    course = StudentCourseMajor.objects.all()
    course_list = []

    # Check if there is DIT Head assigned
    try:
        # Get DIT Head
        get_department_head = User.objects.get(is_department_head=1)
    except:
        print("No DIT Head assigned")

        context = {
            "form": form, 
            "response": "sweet no dit head assigned"}

        return render(request, "signup.html", context)

    

    # Get All Panel
    panel_members = User.objects.all().filter(is_panel=1)

    # Get All Adviser
    adviser = User.objects.all().filter(is_adviser=1)

    # Get All Subject Teachers
    subject_teachers = User.objects.all().filter(is_subject_teacher=1)
    subject_teacher_list = []

    # Get All Academic Affairs
    academic_affairs = User.objects.all().filter(is_academic_affairs=1)

    # Get All Library
    library = User.objects.all().filter(is_library=1)

    # Get All Research & Extension
    research_extension = User.objects.all().filter(is_research_extension=1)

    print(panel_members.count())

    # Check if there are no available course
    if not course:
        print("No Course Available")

        context = {
            "form": form, 
            "response": "sweet no course available"}

        return render(request, "signup.html", context)

    else:
        for course_abbr in course:
            course_list.append(course_abbr.course_major_abbr)

    # Check if there are no Panel Members assigned
    if not panel_members:
        print("No Panel assigned")

        context = {
            "form": form, 
            "response": "sweet no panel assigned"}

        return render(request, "signup.html", context)

    else:
        pass

    # Check if Panel Members is incomplete
    if panel_members.count() < 6:
        print("Incomplete Panel Members")

        context = {
            "form": form, 
            "response": "sweet incomplete panel"}

        return render(request, "signup.html", context)

    else:
        pass

    # Check if there are no subject teacher assigned
    if not subject_teachers:
        print("No Subject Teachers assigned")

        context = {
            "form": form, "response": "sweet no subject teacher assigned"
            }

        return render(request, "signup.html", context)

    else:
        for subject_teacher in subject_teachers:

            subject_teacher_full_name = None

            if subject_teacher.middle_name == "":
                subject_teacher_full_name = subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.last_name + " " + subject_teacher.suffix
                subject_teacher_list.append(subject_teacher_full_name)
            else:
                subject_teacher_full_name = subject_teacher.honorific + " " + subject_teacher.first_name + " " + subject_teacher.middle_name[0] + ". " + subject_teacher.last_name + " " + subject_teacher.suffix
                subject_teacher_list.append(subject_teacher_full_name)

        print("Available Course: ", course_list)
        print("Available Subject Teachers: ", subject_teacher_list)

        subject_teacher_list.sort()


    # Check if there are no Adviser assigned
    if not adviser:
        print("No Adviser assigned")

        context = {
            "form": form, 
            "response": "sweet no adviser assigned"}

        return render(request, "signup.html", context)

    else:
        pass

    # Check if there are no Academic Affairs assigned
    if not academic_affairs:
        print("No Academic Affairs assigned")

        context = {
            "form": form, 
            "response": "sweet no academic affairs assigned"}

        return render(request, "signup.html", context)

    else:
        pass

    # Check if there are no Library assigned
    if not library:
        print("No Library assigned")

        context = {
            "form": form, 
            "response": "sweet no library assigned"}

        return render(request, "signup.html", context)

    else:
        pass

    # Check if there are no Research & Extension assigned
    if not research_extension:
        print("No Research & Extension assigned")

        context = {
            "form": form, 
            "response": "sweet no research extension assigned"}

        return render(request, "signup.html", context)

    else:
        pass


    if request.method == "POST":
        form = SignUpForm(request.POST)

        suffix_input = request.POST.get("suffix_input")
        course_input = request.POST.get("course_input")
        subject_teacher_input = request.POST.get("subject_teacher_input")
        confirm_password = request.POST.get("confirm_password_input")

        if suffix_input not in suffix_list:

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "sweet invalid suffix"}

            return render(request, "signup.html", context)

        if course_input == "default":

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "choose course"}

            return render(request, "signup.html", context)

        if course_input not in course_list:

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "sweet invalid course"}

            return render(request, "signup.html", context)

        if subject_teacher_input == "default":

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "choose subject teacher"}

            return render(request, "signup.html", context)

        if subject_teacher_input not in course_list:

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "sweet invalid subject teacher"}

        if form.is_valid():
            print("Valid form")

            user = form.save(commit=False)

            user_username_input = user.username
            user_email_input = user.email
            print(user_username_input)

            # Check if the Username is already part of a group
            try:
                student_member_check = StudentGroupMember.objects.get(student_member_username=user_username_input)
                print("User exist")

                context = {
                    "form": form,
                    "course": course,
                    "subject_teachers": subject_teachers,
                    "student_member_check_username": student_member_check.student_member_username,
                    "student_member_check_name": student_member_check.student_member_full_name,
                    "response": "sweet user exist",
                }
                return render(request, "signup.html", context)

            except:
                pass

            # Check if the Username is valid
            if "TUPC" in user_username_input:
                pass

            else:
                context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "invalid username"}
                return render(request, "signup.html", context)

            if "gsfe.tupcavite.edu.ph" in user_email_input:
                pass

            else:
                context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "invalid email"}
                return render(request, "signup.html", context)

            if user.password == confirm_password:
                print("Match password")

                user.save()

                user_check = User.objects.get(username=user.username)
                user_check.first_name = request.POST.get("first_name_input").title()
                user_check.middle_name = request.POST.get("middle_name_input").title()
                user_check.last_name = request.POST.get("last_name_input").title()
                user_check.suffix = request.POST.get("suffix_input")
                user_check.department = "Industrial Technology"
                user_check.user_account = "Student"
                user_check.is_student = 1
                user_check.save()

                course_data = StudentCourseMajor.objects.get(course_major_abbr=request.POST.get("course_input"))

                print(subject_teacher_input)
                subject_teacher_data = User.objects.get(username=subject_teacher_input)

                subject_teacher_full_name = None

                if subject_teacher_data.middle_name == "":
                    subject_teacher_full_name = subject_teacher_data.honorific + " " + subject_teacher_data.first_name + " " + subject_teacher_data.last_name + " " + subject_teacher_data.suffix

                else:
                    subject_teacher_full_name = subject_teacher_data.honorific + " " + subject_teacher_data.first_name + subject_teacher_data.middle_name[0] + ". " + subject_teacher_data.last_name + " " + subject_teacher_data.suffix

                student_leader = StudentLeader(
                    username=user_check.username,
                    email=user_check.email,
                    first_name=request.POST.get("first_name_input").title(),
                    middle_name=request.POST.get("middle_name_input").title(),
                    last_name=request.POST.get("last_name_input").title(),
                    suffix=suffix_input,
                    department="Industrial Technology",
                    course=course_data.course,
                    major=course_data.major,
                    course_major_abbr=course_data.course_major_abbr,
                    group_count=0,
                    bet3_subject_teacher_username=subject_teacher_data.username,
                    bet3_subject_teacher_name=subject_teacher_full_name,
                    bet3_status="Ongoing",
                    current_subject="BET-3",
                    request_limit=5,
                )

                student_leader.save()

                login(request, user)
                return redirect("student-dashboard")

            else:
                print("Mismatch password")

                context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "password mismatch"}
                return render(request, "signup.html", context)

        else:
            print("Invalid form")

            context = {"form": form, "course": course, "subject_teachers": subject_teachers, "response": "invalid form"}
            return render(request, "signup.html", context)

    context = {
        "form": form,
        "course": course,
        "subject_teachers": subject_teachers,
    }

    return render(request, "signup.html", context)


# Index / Log in Page
def forgotPassword(request):

    if request.method == "POST":
        # Get data from Front-end
        email_input = request.POST.get("email_input")

        if "gsfe.tupcavite.edu.ph" in email_input:
            pass

        else:
            context = {"response": "sweet invalid email"}
            return render(request, "forgot-password.html", context)

        # Check if the user exist
        try:
            user_check = User.objects.get(email=email_input)

            S = 10
            generated_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))    
            print(str(generated_token)) # print the random data 

            create_token = ForgotPassword(
                username = user_check.username,
                token = str(generated_token),
            )
            create_token.save()

            try:
                get_token = ForgotPassword.objects.get(username = user_check.username)

                # Send g-mail notifications
                send_mail(
                    "TUPC Research Defense Web App - Forgot Password",
                    "Good Day " + user_check.username + ",\n" +"You have requested to reset your password, here is the link to reset your password. \n Please don't give this link to anyone. Thank you and Have a nice day. \n" + "http://127.0.0.1:8000/reset-password/" + get_token.token,
                    "unofficial.tupc.uitc@gmail.com",
                    [user_check.email],
                    fail_silently=False,
                )

                context = {"response": "sweet email sent"}
                return render(request, "login.html", context)

            except:
                context = {"response": "sweet user error"}
                return render(request, "forgot-password.html", context)



           
        # If the user doesn't exist
        except:
            print("The User doesn't exist.")

            context = {"response": "sweet email not found"}
            return render(request, "forgot-password.html", context)

    return render(request, "forgot-password.html")


def resetPassword(request, id):

    try:
        check_token = ForgotPassword.objects.get(token = id)
    except:
        return redirect("login")

    if request.method == "POST":
        new_password = request.POST.get("new_password_input")
        confirm_new_password = request.POST.get("confirm_new_password_input")

        if new_password != confirm_new_password:
            context = {"response": "sweet password mismatch"}
            return render(request, "reset-password.html", context)
        
        User.objects.filter(username = check_token.username).update(password = new_password)
        check_token.delete()


        context = {"response": "sweet password changed"}
        return render(request, "login.html", context)



    return render(request, "reset-password.html")

# Log out
def logout_user(request):
    currently_loggedin_user = request.user

    if currently_loggedin_user.is_student == 1:
        file_paths = []

        get_file_paths = FilePath.objects.all().filter(student_leader_username=currently_loggedin_user.username)

        for file_path in get_file_paths:
            file_paths.append(file_path.file_path)

        print(file_paths)

        for i in range(len(file_paths)):
            if os.path.isfile(file_paths[i]):
                os.remove(file_paths[i])
                print("Panel Invitation BET-3 has been deleted")
            else:
                print("Panel Invitation BET-3 does not exist")
            i + 1

        FilePath.objects.all().filter(student_leader_username=currently_loggedin_user.username).delete()

    # if currently_loggedin_user.is_department_head == 1:
    #     # Check if E-Sign Exist
    #     if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png"):
    #         os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png")
    #         print("E-Sign Deleted")

    # if currently_loggedin_user.is_panel == 1:
    #     # Check if E-Sign Exist
    #     if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png"):
    #         os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png")
    #         print("E-Sign Deleted")

    # if currently_loggedin_user.is_adviser == 1:
    #     # Check if E-Sign Exist
    #     if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png"):
    #         os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png")
    #         print("E-Sign Deleted")

    # if currently_loggedin_user.is_subject_teacher == 1:
    #     # Check if E-Sign Exist
    #     if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png"):
    #         os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/"+str(currently_loggedin_user)+".png")
    #         print("E-Sign Deleted")

    logout(request)
    return redirect("login")


# Index / Log in Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def login_as_user_accounts(request):
    currently_loggedin_user = request.user

    if currently_loggedin_user.is_department_head == 1:
        context = {
            "is_department_head": "1",
        }
        return render(request, "login-as-user-accounts.html", context)
    else:
        return render(request, "login-as-user-accounts.html")


@login_required(login_url="login")
def topbarProcess(request):

    currently_loggedin_user = request.user
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
        currently_loggedin_user_account = "Student"

    elif currently_loggedin_user.is_administrator == 1:
        currently_loggedin_user_account = "Administrator"

    elif currently_loggedin_user.is_academic_affairs == 1:
        currently_loggedin_user_account = "Academic Affairs"

    elif currently_loggedin_user.is_library == 1:
        currently_loggedin_user_account = "Library"

    elif currently_loggedin_user.is_research_extension == 1:
        currently_loggedin_user_account = "Research & Extension"

    return (currently_loggedin_user_full_name, currently_loggedin_user_account)


@login_required(login_url="login")
def fullNameProcess(request, id):

    print(id)

    faculty_full_name = ""

    try:
        get_faculty_data = User.objects.get(username=id)
        print("pass")

    except:
        return faculty_full_name

    if get_faculty_data.middle_name == "":
        faculty_full_name = get_faculty_data.honorific + " " + get_faculty_data.first_name + " " + get_faculty_data.last_name + " " + get_faculty_data.suffix
        return faculty_full_name
    else:
        faculty_full_name = get_faculty_data.honorific + " " + get_faculty_data.first_name + " " + get_faculty_data.middle_name[0] + ". " + get_faculty_data.last_name + " " + get_faculty_data.suffix
        return faculty_full_name
