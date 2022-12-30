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

today = date.today()
date_today = today.strftime("%B %d, %Y")

##########################################################################################################################

# Index / Log in Page
def index(request):

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
                return render(request, "index.html", context)

        # If the user doesn't exist
        except:
            print("The User doesn't exist.")

            context = {"response": "user does not exist"}
            return render(request, "index.html", context)

    return render(request, "index.html")


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
    return redirect("index")


# Index / Log in Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def login_as_user_accounts(request):
    currently_loggedin_user = request.user

    if currently_loggedin_user.is_department_head == 1:
        context = {
            "is_department_head": "1",
        }
        return render(request, "login-as-user-accounts.html", context)
    else:
        return render(request, "login-as-user-accounts.html")


# Academic Affairs Office
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def academicAffairsOfficeDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,

    }

    return render(request, "academic-affairs-office-dashboard.html", context)


# Library
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_library, login_url="index")
def libraryDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
          "date_today": date_today,
    }

    return render(request, "library-dashboard.html", context)


# Research & Extension
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_receipt = AcknowledgementReceipt.objects.all().filter(research_ext_response ="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "pending_receipt": get_pending_receipt,
    }

    return render(request, "research-extension-dashboard.html", context)


# Research & Extension - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionProfile(request):
    currently_loggedin_user = request.user

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        esignature_exist = "True"
        print("E-sign exist")

    else:
        esignature_exist = "False"
        print("E-sign doesn't exist.")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": currently_loggedin_user,
        "currently_loggedin_user_first_name": currently_loggedin_user.first_name,
        "currently_loggedin_user_middle_name": currently_loggedin_user.middle_name,
        "currently_loggedin_user_last_name": currently_loggedin_user.last_name,
        "currently_loggedin_user_department": currently_loggedin_user.department,
        "currently_loggedin_username": currently_loggedin_user.username,
        "currently_loggedin_user_email": currently_loggedin_user.email,
        "esignature_exist": esignature_exist,
    }

    return render(request, "research-extension-profile.html", context)


# Panel - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionUploadESignature(request):
    currently_loggedin_user = request.user

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        esignature_exist = "True"
        print("E-sign exist")

    else:
        esignature_exist = "False"
        print("E-sign doesn't exist.")

    if request.method == "POST":
        esignature = request.FILES["esignature"]
        print(esignature.name)

        get_file_extensions = os.path.splitext(esignature.name)
        print(get_file_extensions[1])

        if get_file_extensions[1] == ".png":
            print("Valid")

            if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1]):
                os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1])

                fs = FileSystemStorage()

                filename = fs.save(str(currently_loggedin_user) + get_file_extensions[1], esignature)
                uploaded_file_url = fs.url(filename)
                print(uploaded_file_url)

                esignature_size = cv2.imread("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1])
                h, w, c = esignature_size.shape

                print("width:  ", w)
                print("height: ", h)
                print("channel:", c)

                if w == 300 and h == 100:
                    print("Valid Size")
                else:
                    print("Invalid Size")
                    # Invalid - Delete E-Signature
                    os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1])

                    context = {
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_data": currently_loggedin_user,
                        "currently_loggedin_user_first_name": currently_loggedin_user.first_name,
                        "currently_loggedin_user_middle_name": currently_loggedin_user.middle_name,
                        "currently_loggedin_user_last_name": currently_loggedin_user.last_name,
                        "currently_loggedin_user_department": currently_loggedin_user.department,
                        "currently_loggedin_username": currently_loggedin_user.username,
                        "currently_loggedin_user_email": currently_loggedin_user.email,
                        "esignature_exist": esignature_exist,
                        "response": "sweet invalid size",
                    }

                    return render(request, "research-extension-profile.html", context)
            else:
                print("The file does not exist")

                fs = FileSystemStorage()

                filename = fs.save(str(currently_loggedin_user) + get_file_extensions[1], esignature)
                uploaded_file_url = fs.url(filename)
                print(uploaded_file_url)

                esignature_size = cv2.imread("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1])
                h, w, c = esignature_size.shape

                if w == 300 and h == 100:
                    print("Valid Size")
                else:
                    print("Invalid Size")
                    # Invalid - Delete E-Signature
                    os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + get_file_extensions[1])

                    context = {
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_data": currently_loggedin_user,
                        "currently_loggedin_user_first_name": currently_loggedin_user.first_name,
                        "currently_loggedin_user_middle_name": currently_loggedin_user.middle_name,
                        "currently_loggedin_user_last_name": currently_loggedin_user.last_name,
                        "currently_loggedin_user_department": currently_loggedin_user.department,
                        "currently_loggedin_username": currently_loggedin_user.username,
                        "currently_loggedin_user_email": currently_loggedin_user.email,
                        "esignature_exist": esignature_exist,
                        "response": "sweet invalid size",
                    }

                    return render(request, "research-extension-profile.html", context)

                return redirect("research-extension-profile")

        else:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_data": currently_loggedin_user,
                "currently_loggedin_user_first_name": currently_loggedin_user.first_name,
                "currently_loggedin_user_middle_name": currently_loggedin_user.middle_name,
                "currently_loggedin_user_last_name": currently_loggedin_user.last_name,
                "currently_loggedin_user_department": currently_loggedin_user.department,
                "currently_loggedin_username": currently_loggedin_user.username,
                "currently_loggedin_user_email": currently_loggedin_user.email,
                "esignature_exist": esignature_exist,
                "response": "sweet not png",
            }

            return render(request, "research-extension-profile.html", context)


# Panel - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("research-extension-profile")


# Panel - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionCreateESignature(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    if request.method == "POST":
        signature_url = request.POST.get("signature_link")

        # Separate the metadata from the image data
        head, data = signature_url.split(",", 1)

        # Get the file extension (gif, jpeg, png)
        file_ext = head.split(";")[0].split("/")[1]

        # Decode the image data
        plain_data = base64.b64decode(data)

        # # Write the image to a file
        with open("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + currently_loggedin_user.username + "." + file_ext, "wb") as f:
            f.write(plain_data)

        return redirect("research-extension-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "research-extension-signature-pad.html", context)


# Panel - Acount Settings Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionAccountSettings(request):
    currently_loggedin_user = request.user

    currently_loggedin_user_middle_name = currently_loggedin_user.middle_name
    currently_loggedin_user_middle_initial = None

    currently_loggedin_user_full_name = None

    if currently_loggedin_user_middle_name == "":
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user_middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": currently_loggedin_user,
    }

    if request.method == "POST":
        current_password_input = request.POST.get("current_password_input")
        new_password_input = request.POST.get("new_password_input")
        confirm_new_password_input = request.POST.get("confirm_new_password_input")

        if current_password_input == currently_loggedin_user.password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=currently_loggedin_user.username).update(password=new_password_input)

                    context = {"response": "changed password"}
                    return render(request, "index.html", context)

                else:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "new password and confirm new password doesnt match"}

                    return render(request, "research-extension-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "research-extension-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "research-extension-account-settings.html", context)

    return render(request, "research-extension-account-settings.html", context)


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(research_ext_response ="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": date_today,
            "pending_receipt": get_pending_receipt,
             "response": "sweet no esign",
        }



    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.research_ext_username = currently_loggedin_user.username
        check_receipt.research_ext_full_name = currently_loggedin_user_full_name
        check_receipt.research_ext_response = "Accepted"
        check_receipt.research_ext_response_date = date_today
        check_receipt.research_ext_signature = True

        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Research & Extension) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(research_ext_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel conforme accepted",
            }

        return render(request, "research-extension-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("research-extension-dashboard")


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_research_extension, login_url="index")
def researchExtensionAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.research_ext_username = currently_loggedin_user.username
        check_receipt.research_ext_full_name = currently_loggedin_user_full_name
        check_receipt.research_ext_response = "Accepted"
        check_receipt.research_ext_response_date = date_today

        check_receipt.save()

        print("pass -save")

        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Research & Extension) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(research_ext_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel conforme accepted",
            }

        return render(request, "research-extension-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("research-extension-dashboard")


@login_required(login_url="index")
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


@login_required(login_url="index")
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
