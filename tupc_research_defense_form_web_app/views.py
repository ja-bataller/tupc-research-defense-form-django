from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
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

##########################################################################################################################

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

    course = StudentCourseMajor.objects.all()
    subject_teachers = User.objects.all().filter(is_subject_teacher=1)

    course_list = []

    subject_teacher_list = []

    if not course:
        print("No Course Available")

        context = {"form": form, "response": "sweet incomplete form"}

        return render(request, "signup.html", context)

    else:
        for course_abbr in course:
            course_list.append(course_abbr.course_major_abbr)

    if not subject_teachers:
        print("No Subject Teachers Available")

        context = {"form": form, "response": "sweet incomplete form"}

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

            # Check if the Username is already part of a group
            try:
                student_member_check = StudentGroupMember.objects.get(student_member_username=user_username_input)
                print("User exist")

                context = {
                    "form": form,
                    "course": course,
                    "subject_teachers": subject_teachers,
                    "student_member_check_username": student_member_check.student_member_username,
                    "student_member_check_name": student_member_check.student_member_name,
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


##########################################################################################################################

# Student - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentDashboard(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("logout")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "date_today": date_today,
    }

    return render(request, "student-dashboard.html", context)


# Student - User Profile - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentProfile(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get the currently logged in user data
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
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "user_first_name": user_first_name,
        "user_middle_name": user_middle_name,
        "user_last_name": user_last_name,
        "user_suffix": user_suffix,
        "user_course": user_course,
        "course_name": course_name,
        "major_name": major_name,
        "username": user_username,
        "user_email": user_email,
    }

    if request.method == "POST":
        current_password_input = request.POST.get("current_password_input")
        new_password_input = request.POST.get("new_password_input")
        confirm_new_password_input = request.POST.get("confirm_new_password_input")

        if current_password_input == current_password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {"response": "changed password"}
                    return render(request, "index.html", context)

                else:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "user_course": user_course, "course_name": course_name, "major_name": major_name, "username": user_username, "user_email": user_email, "response": "new password and confirm new password doesnt match"}

                    return render(request, "student-profile.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "user_course": user_course, "course_name": course_name, "major_name": major_name, "username": user_username, "user_email": user_email, "response": "current password and new password is same"}

                return render(request, "student-profile.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "user_course": user_course, "course_name": course_name, "major_name": major_name, "username": user_username, "user_email": user_email, "response": "current password is incorrect"}

            return render(request, "student-profile.html", context)

    return render(request, "student-profile.html", context)


# Student - Group Member - Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentGroupMemberProcess(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)

    except:
        return redirect("index")

    if get_student_leader_data.group_members_status == "completed":
        return redirect("student-group-members-dashboard")
    else:
        return redirect("student-add-group-members")


# Student - Add Group Member - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentAddGroupMember(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)

    except:
        return redirect("index")

    if get_student_leader_data.group_members_status == "completed":
        return redirect("student-group-members-dashboard")

    suffix_list = ["", "Sr.", "Jr.", "I", "II", "III", "IV", "V"]

    if request.method == "POST":
        group_member_count = request.POST.get("group_member_count")

        student_username_2 = request.POST.get("student_username_2")
        student_first_name_2 = request.POST.get("student_first_name_2")
        student_middle_name_2 = request.POST.get("student_middle_name_2")
        student_last_name_2 = request.POST.get("student_last_name_2")
        student_suffix_2 = request.POST.get("student_suffix_2")

        student_username_3 = request.POST.get("student_username_3")
        student_first_name_3 = request.POST.get("student_first_name_3")
        student_middle_name_3 = request.POST.get("student_middle_name_3")
        student_last_name_3 = request.POST.get("student_last_name_3")
        student_suffix_3 = request.POST.get("student_suffix_3")

        student_username_4 = request.POST.get("student_username_4")
        student_first_name_4 = request.POST.get("student_first_name_4")
        student_middle_name_4 = request.POST.get("student_middle_name_4")
        student_last_name_4 = request.POST.get("student_last_name_4")
        student_suffix_4 = request.POST.get("student_suffix_4")

        student_username_5 = request.POST.get("student_username_5")
        student_first_name_5 = request.POST.get("student_first_name_5")
        student_middle_name_5 = request.POST.get("student_middle_name_5")
        student_last_name_5 = request.POST.get("student_last_name_5")
        student_suffix_5 = request.POST.get("student_suffix_5")

        # Student Leader Full Name
        if get_student_leader_data.middle_name == "":
            student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
        else:
            student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

        if group_member_count == "1":
            get_student_leader_data.group_count = 1
            get_student_leader_data.save()

            get_student_leader_data.group_members_status = "completed"
            get_student_leader_data.save()

            get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "student_leader_full_name": student_leader_full_name, "group_members": get_group_members, "response": "sweet no group members"}
            return render(request, "student-group-member-dashboard.html", context)

        else:

            if student_username_2 != "":
                student_member_full_name_2 = None

                if "TUPC-" not in student_username_2:

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid username"}
                    return render(request, "student-add-group-member.html", context)

                if student_suffix_2 not in suffix_list:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid suffix"}
                    return render(request, "student-add-group-member.html", context)

                # Student - Check if TUPC ID No is the same with the other group members.
                if student_username_2 in {current_user.username, student_username_3, student_username_4, student_username_5}:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet group member has same username"}

                    return render(request, "student-add-group-member.html", context)

                # Student - Check if Group Member is Student Leader.
                try:
                    User.objects.get(username=student_username_2)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_2, "response": "sweet group member is a student leader"}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                # Student - Check if Group Member is a group member.
                try:
                    StudentGroupMember.objects.get(student_member_username=student_username_2)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_2, "response": "sweet already group member "}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                if student_middle_name_2 == "":
                    student_member_full_name_2 = student_last_name_2 + " " + student_suffix_2 + ", " + student_first_name_2
                else:
                    student_member_full_name_2 = student_last_name_2 + " " + student_suffix_2 + ", " + student_first_name_2 + " " + student_middle_name_2[0] + "."

                save_group_member_2 = StudentGroupMember(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name.title(),
                    student_member_username=student_username_2,
                    student_member_full_name=student_member_full_name_2.title(),
                    course=get_student_leader_data.course,
                    major=get_student_leader_data.major,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                )
                save_group_member_2.save()

                get_student_leader_data.group_count = 2
                get_student_leader_data.save()

            if student_username_3 != "":
                student_member_full_name_3 = None

                if "TUPC-" not in student_username_3:

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid username"}
                    return render(request, "student-add-group-member.html", context)

                if student_suffix_3 not in suffix_list:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid suffix"}
                    return render(request, "student-add-group-member.html", context)

                # Student - Check if TUPC ID No is the same with the other group members.
                if student_username_3 in {current_user.username, student_username_2, student_username_4, student_username_5}:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet group member has same username"}

                    return render(request, "student-add-group-member.html", context)

                # Student - Check if Group Member is Student Leader.
                try:
                    User.objects.get(username=student_username_3)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_3, "response": "sweet group member is a student leader"}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                # Student - Check if Group Member is a group member.
                try:
                    StudentGroupMember.objects.get(student_member_username=student_username_3)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_3, "response": "sweet already group member "}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                if student_middle_name_3 == "":
                    student_member_full_name_3 = student_last_name_3 + " " + student_suffix_3 + ", " + student_first_name_3
                else:
                    student_member_full_name_3 = student_last_name_3 + " " + student_suffix_3 + ", " + student_first_name_3 + " " + student_middle_name_3[0] + "."

                save_group_member_3 = StudentGroupMember(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name.title(),
                    student_member_username=student_username_3,
                    student_member_full_name=student_member_full_name_3.title(),
                    course=get_student_leader_data.course,
                    major=get_student_leader_data.major,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                )
                save_group_member_3.save()

                get_student_leader_data.group_count = 3
                get_student_leader_data.save()

            if student_username_4 != "":
                student_member_full_name_4 = None

                if "TUPC-" not in student_username_4:

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid username"}
                    return render(request, "student-add-group-member.html", context)

                if student_suffix_4 not in suffix_list:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid suffix"}
                    return render(request, "student-add-group-member.html", context)

                # Student - Check if TUPC ID No is the same with the other group members.
                if student_username_4 in {current_user.username, student_username_2, student_username_3, student_username_5}:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet group member has same username"}

                    return render(request, "student-add-group-member.html", context)

                # Student - Check if Group Member is Student Leader.
                try:
                    User.objects.get(username=student_username_4)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_4, "response": "sweet group member is a student leader"}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                # Student - Check if Group Member is a group member.
                try:
                    StudentGroupMember.objects.get(student_member_username=student_username_4)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_4, "response": "sweet already group member "}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                if student_middle_name_4 == "":
                    student_member_full_name_4 = student_last_name_4 + " " + student_suffix_4 + ", " + student_first_name_4
                else:
                    student_member_full_name_4 = student_last_name_4 + " " + student_suffix_4 + ", " + student_first_name_4 + " " + student_middle_name_4[0] + "."

                save_group_member_4 = StudentGroupMember(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name.title(),
                    student_member_username=student_username_4,
                    student_member_full_name=student_member_full_name_4.title(),
                    course=get_student_leader_data.course,
                    major=get_student_leader_data.major,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                )
                save_group_member_4.save()

                get_student_leader_data.group_count = 4
                get_student_leader_data.save()

            if student_username_5 != "":
                student_member_full_name_5 = None

                if "TUPC-" not in student_username_5:

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid username"}
                    return render(request, "student-add-group-member.html", context)

                if student_suffix_5 not in suffix_list:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet invalid suffix"}
                    return render(request, "student-add-group-member.html", context)

                # Student - Check if TUPC ID No is the same with the other group members.
                if student_username_5 in {current_user.username, student_username_2, student_username_3, student_username_4}:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet group member has same username"}

                    return render(request, "student-add-group-member.html", context)

                # Student - Check if Group Member is Student Leader.
                try:
                    User.objects.get(username=student_username_5)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_5, "response": "sweet group member is a student leader"}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                # Student - Check if Group Member is a group member.
                try:
                    StudentGroupMember.objects.get(student_member_username=student_username_5)

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "existing_username": student_username_5, "response": "sweet already group member "}

                    return render(request, "student-add-group-member.html", context)

                except:
                    pass

                if student_middle_name_5 == "":
                    student_member_full_name_5 = student_last_name_5 + " " + student_suffix_5 + ", " + student_first_name_5
                else:
                    student_member_full_name_5 = student_last_name_5 + " " + student_suffix_5 + ", " + student_first_name_5 + " " + student_middle_name_5[0] + "."

                save_group_member_5 = StudentGroupMember(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name.title(),
                    student_member_username=student_username_5,
                    student_member_full_name=student_member_full_name_5.title(),
                    course=get_student_leader_data.course,
                    major=get_student_leader_data.major,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                )
                save_group_member_5.save()

                get_student_leader_data.group_count = 5
                get_student_leader_data.save()

        get_student_leader_data.group_members_status = "completed"
        get_student_leader_data.save()
        get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "student_leader_full_name": student_leader_full_name, "group_members": get_group_members, "response": "sweet group members added"}

        return render(request, "student-group-member-dashboard.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
    }

    return render(request, "student-add-group-member.html", context)


# Student - Group Member - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentGroupMembersDashboard(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)

    except:
        return redirect("index")

    if get_student_leader_data.group_members_status != "completed":
        return redirect("student-add-group-members")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)

    student_leader_full_name = None

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0]

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
    }

    return render(request, "student-group-member-dashboard.html", context)


# Student - Research Title - Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentResearchTitleProcess(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)

    except:
        return redirect("index")

    if get_student_leader_data.research_titles_status == "completed":
        return redirect("student-research-title-dashboard")
    else:
        return redirect("student-add-research-titles")


# Student - Add Research Title - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentAddResearchTitle(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)

    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status == "completed":
        return redirect("student-research-title-dashboard")
    ############## PAGE VALIDATION ##############

    # Student Leader Full Name
    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    research_titles = []

    if request.method == "POST":
        research_title_1_input = request.POST.get("research_title_1_input")
        research_title_2_input = request.POST.get("research_title_2_input")
        research_title_3_input = request.POST.get("research_title_3_input")
        research_title_4_input = request.POST.get("research_title_4_input")
        research_title_5_input = request.POST.get("research_title_5_input")

        if research_title_1_input != "":

            if research_title_1_input in (research_title_2_input, research_title_3_input, research_title_4_input, research_title_5_input):
                print("pass 1")
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet same research title"}

                return render(request, "student-add-research-title.html", context)

            try:
                ResearchTitle.objects.get(research_title=research_title_1_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_1_input.title, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            try:
                ResearchTitleLog.objects.get(research_title=research_title_1_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_1_input.title, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            research_titles.append(research_title_1_input)

        if research_title_2_input != "":

            if research_title_2_input in {research_title_1_input, research_title_3_input, research_title_4_input, research_title_5_input}:

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet same research title"}
                return render(request, "student-add-research-title.html", context)

            try:
                ResearchTitle.objects.get(research_title=research_title_2_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_2_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            try:
                ResearchTitleLog.objects.get(research_title=research_title_2_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_2_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            research_titles.append(research_title_2_input)

        if research_title_3_input != "":

            if research_title_3_input in {research_title_1_input, research_title_2_input, research_title_4_input, research_title_5_input}:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet same research title"}

                return render(request, "student-add-research-title.html", context)

            try:
                ResearchTitle.objects.get(research_title=research_title_3_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_3_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            try:
                ResearchTitleLog.objects.get(research_title=research_title_3_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_3_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            research_titles.append(research_title_3_input)

        if research_title_4_input != "":

            if research_title_4_input in {research_title_1_input, research_title_2_input, research_title_3_input, research_title_5_input}:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet same research title"}

                return render(request, "student-add-research-title.html", context)

            try:
                ResearchTitle.objects.get(research_title=research_title_4_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_4_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            try:
                ResearchTitleLog.objects.get(research_title=research_title_4_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_4_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            research_titles.append(research_title_4_input)

        if research_title_5_input != "":

            if research_title_5_input in {research_title_1_input, research_title_2_input, research_title_3_input, research_title_4_input}:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet same research title"}

                return render(request, "student-add-research-title.html", context)

            try:
                ResearchTitle.objects.get(research_title=research_title_5_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_5_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            try:
                ResearchTitleLog.objects.get(research_title=research_title_5_input)
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "existing_research_title": research_title_5_input, "response": "sweet research title exist"}
                return render(request, "student-add-research-title.html", context)

            except:
                pass

            research_titles.append(research_title_5_input)

        for i in range(len(research_titles)):
            save_Research_title = ResearchTitle(research_title=research_titles[i].title(), course=get_student_leader_data.course, major=get_student_leader_data.major, course_major_abbr=get_student_leader_data.course_major_abbr, student_leader_username=current_user.username, student_leader_name=student_leader_full_name, status="Title Defense - Pending", date_submitted=today.strftime("%B %d, %Y"))
            save_Research_title.save()
            i + 1

        get_student_leader_data.research_titles_status = "completed"
        get_student_leader_data.save()

        get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "research_titles": get_research_titles, "response": "sweet research title saved"}

        return render(request, "student-research-title-dashboard.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
    }

    return render(request, "student-add-research-title.html", context)


# Student - Research Title - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentResearchTitleDashboard(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        return redirect("student-add-research-titles")
    ############## PAGE VALIDATION ##############

    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "research_titles": get_research_titles}

    return render(request, "student-research-title-dashboard.html", context)


# Student - BET3 - Topic Defense - Panel Invitation - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelInvitationBet3(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)
    ############## PAGE VALIDATION ##############

    get_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    get_accepted_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
    get_pending_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "panel_invitations": get_panel_invitations,
        "accepted_panel_invitations": get_accepted_panel_invitations.count(),
        "pending_panel_invitations": get_pending_panel_invitations.count(),
    }

    return render(request, "student-bet3-panel-invitation-dashboard.html", context)


# Student - BET3 - Topic Defense - Panel Invitation - Create Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelInvitationBet3Create(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)

    if get_student_leader_data.bet3_panel_invitation_status == "completed":
        return redirect("student-panel-invitation-bet3")
    ############## PAGE VALIDATION ##############

    try:
        get_pending_panel_invitation = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")
        pending_count = get_pending_panel_invitation.count()

        get_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        get_accepted_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        get_pending_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

        if int(get_student_leader_data.request_limit) == int(pending_count):
            print("Request Limit Exceed")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet request limit exceed"
            }

            return render(request, "student-bet3-panel-invitation-dashboard.html", context)
    except:
        pass

    panel_members = User.objects.all().filter(is_panel=1)

    defense_dates = DefenseSchedule.objects.all().filter(course=get_student_leader_data.course_major_abbr, username=get_student_leader_data.bet3_subject_teacher_username, status="Available")

    if get_student_leader_data.research_title_defense_date != "":
        pass
    else:
        if not defense_dates:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet no defense schedule"}

            return render(request, "student-bet3-panel-invitation-dashboard.html", context)
        else:
            pass

    defense_date_list = []

    panel_list = []

    # Check if there is DIT Head assigned.
    try:
        dept_head = User.objects.get(is_department_head=1)

        if dept_head.middle_name == "":
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.last_name + " " + dept_head.suffix
        else:
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.middle_name[0] + " " + dept_head.last_name + " " + dept_head.suffix

    except:
        print("No Department Head")

        context = {"response": "sweet no DIT Head"}

        return render(request, "student-panel-invitation-bet-3-create.html", context)

    # Check if there is a Panel assigned.
    if not panel_members or panel_members.count() < 5:
        print("Incomplete Faculty Member")

        context = {"response": "sweet inc panel"}
        return render(request, "student-panel-invitation-bet-3-create.html", context)
    else:
        for panel in panel_members:
            panel_list.append(panel.username)

    for defense_date_id in defense_dates:
        defense_date_list.append(defense_date_id.id)

    student_leader_full_name = None

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if request.method == "POST":
        defense_schedule_input = request.POST.get("defense_schedule_input")
        panel_input = request.POST.get("panel_input")

        # Check if the entered Panel is valid
        if panel_input not in panel_list:

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "response": "sweet invalid panel"}

            return render(request, "student-panel-invitation-bet-3-create.html", context)

        # Check if there are Panel Members assigned
        try:
            get_panel_data = User.objects.get(username=panel_input)

            if get_panel_data.middle_name == "":
                panel_full_name = get_panel_data.honorific + " " + get_panel_data.first_name + " " + get_panel_data.last_name + " " + get_panel_data.suffix
            else:
                panel_full_name = get_panel_data.honorific + " " + get_panel_data.first_name + " " + get_panel_data.middle_name[0] + " " + get_panel_data.last_name + " " + get_panel_data.suffix

        except:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "response": "sweet panel not found"}

            return render(request, "student-panel-invitation-bet-3-create.html", context)

        # Check if the entered Panel Member is Subject Teacher
        try:
            StudentLeader.objects.get(username=current_user.username, bet3_subject_teacher_username=panel_input)

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "panel_full_name": panel_full_name, "response": "sweet subject teacher"}

            return render(request, "student-panel-invitation-bet-3-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Pending Panel Invitation
        try:
            TitlePanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="pending")

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "panel_full_name": panel_full_name, "response": "sweet panel invitation exist"}

            return render(request, "student-panel-invitation-bet-3-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Accepted Panel Invitation
        try:
            TitlePanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="accepted")

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "panel_full_name": panel_full_name, "response": "sweet panel invitation accepted exist"}

            return render(request, "student-panel-invitation-bet-3-create.html", context)
        except:
            pass

        try:
            check_defense_schedule = DefenseSchedule.objects.get(student_leader_username=current_user.username, form = "Research Title Defense")
            print(check_defense_schedule)
            send_panel_invitation = TitlePanelInvitation(
                student_leader_username=current_user.username,
                student_leader_full_name=student_leader_full_name,
                course_major_abbr=get_student_leader_data.course_major_abbr,
                dit_head_username=dept_head.username,
                dit_head_full_name=dept_head_name,
                dit_head_response="pending",
                panel_username=get_panel_data.username,
                panel_full_name=panel_full_name,
                panel_response="on hold",
                research_title_defense_date=check_defense_schedule.date,
                research_title_defense_start_time=check_defense_schedule.start_time,
                research_title_defense_end_time=check_defense_schedule.end_time,
                form_status="pending",
                form_date_sent=date_today,
                form="BET-3 Panel Invitation",
                subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
            )
            send_panel_invitation.save()
            print("Panel Invitation Sent")

        except:
            # Check if the entered Defense Scheduled is valid
            if int(defense_schedule_input) not in defense_date_list:

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "response": "sweet invalid defense schedule"}

                return render(request, "student-panel-invitation-bet-3-create.html", context)
            else:

                # Save Defense Schedule Table
                try:
                    save_defense_schedule = DefenseSchedule.objects.get(id=int(defense_schedule_input))

                    save_defense_schedule.student_leader_username = current_user.username
                    save_defense_schedule.student_leader_name = student_leader_full_name
                    save_defense_schedule.status = "Reserved"
                    save_defense_schedule.save()
                    print("Defense Schedule Data Updated")

                except:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "response": "sweet defense schedule not found"}

                    return render(request, "student-panel-invitation-bet-3-create.html", context)

                get_student_leader_data.research_title_defense_date = save_defense_schedule.date
                get_student_leader_data.research_title_defense_start_time = save_defense_schedule.start_time
                get_student_leader_data.research_title_defense_end_time = save_defense_schedule.end_time
                get_student_leader_data.save()
                print("Student Leader Data Updated")

                send_panel_invitation = TitlePanelInvitation(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                    dit_head_username=dept_head.username,
                    dit_head_full_name=dept_head_name,
                    dit_head_response="pending",
                    panel_username=get_panel_data.username,
                    panel_full_name=panel_full_name,
                    panel_response="on hold",
                    research_title_defense_date=save_defense_schedule.date,
                    research_title_defense_start_time=save_defense_schedule.start_time,
                    research_title_defense_end_time=save_defense_schedule.end_time,
                    form_status="pending",
                    form_date_sent=today.strftime("%B %d, %Y"),
                    form="BET-3 Panel Invitation",
                    subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                    subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
                )
                send_panel_invitation.save()
                print("Panel Invitation Sent")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "dept_head_name": dept_head_name, "panel_members": panel_members, "defense_dates": defense_dates, "response": "sweet panel invitation sent"}

        return render(request, "student-panel-invitation-bet-3-create.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "dept_head_name": dept_head_name,
        "panel_members": panel_members,
        "defense_dates": defense_dates,
    }

    return render(request, "student-panel-invitation-bet-3-create.html", context)


# Student - BET3 - Topic Defense - Panel Invitation - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelInvitationBet3Save(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)
    ############## PAGE VALIDATION ##############

    get_student_leader_data.bet3_panel_invitation_status = "completed"
    get_student_leader_data.save()

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "response": "sweet bet-3 panel invitation saved"}

    return render(request, "student-bet3-panel-invitation-dashboard.html", context)


# Student - BET3 - Topic Defense - Panel Invitation - Download Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentDownloadPanelInvitationBet3(request, id):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
        get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
        get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)
        get_panel_invitation = TitlePanelInvitation.objects.get(id=int(id), student_leader_username=current_user.username)

    except:
        return redirect("student-panel-invitation-bet3")

    ############## BET-3 PANEL INVITATION DATA ##############
    date_submitted = get_panel_invitation.form_date_sent

    student_member_list = [get_panel_invitation.student_leader_full_name]
    course = get_student_leader_data.course.replace("Engineering", "Eng.")
    major = get_student_leader_data.major

    research_title_list = []

    defense_date = get_panel_invitation.research_title_defense_date
    defense_start_time = get_panel_invitation.research_title_defense_start_time
    defense_end_time = get_panel_invitation.research_title_defense_end_time

    dit_head_full_name = get_panel_invitation.dit_head_full_name
    dit_head_response = get_panel_invitation.dit_head_response
    dit_head_response_date = get_panel_invitation.dit_head_response_date

    panel_full_name = get_panel_invitation.panel_full_name
    panel_username = get_panel_invitation.panel_username
    panel_response = get_panel_invitation.panel_response
    panel_response_date = get_panel_invitation.panel_response_date
    ############## BET-3 PANEL INVITATION DATA ##############

    if get_group_members:
        for group_member in get_group_members:
            student_member_list.append(group_member.student_member_full_name)

    student_member_list.sort()

    if get_research_titles:
        for research_title in get_research_titles:
            research_title_list.append(research_title.research_title)

    print("Date Sent: ", date_submitted)

    print("Group Members: ", student_member_list)
    print("Course: ", course)
    print("Major: ", major)
    print("Research Titles: ", research_title_list)

    print("Defense Date: ", defense_date)
    print("Defense Start Time: ", defense_start_time)
    print("Defense End Time: ", defense_end_time)

    print("DIT Head Name: ", dit_head_full_name)
    print("DIT Head Response: ", dit_head_response)
    print("DIT Head Response Date: ", dit_head_response_date)

    print("Panel Name: ", panel_full_name)
    print("Panel Response: ", panel_response)
    print("Panel Response Date: ", panel_response_date)

    doc = Document("static/forms/1-TOPIC-DEFENSE-PANEL-INVITATION.docx")
    # doc = Document('/home/johnanthonybataller/tupc-research-defense-form-django/static/forms/1-TOPIC-DEFENSE-PANEL-INVITATION.docx')

    student_table = doc.tables[0] # Student Data Table
    panel_table = doc.tables[3] # Panel Data Table
    head_signature_table = doc.tables[1]
    panel_signature_table= doc.tables[2]

    qr_code_box = doc.tables[4]

    try:
        student_table.cell(1, 0).paragraphs[0].runs[0].text = student_member_list[0]
        student_table.cell(1, 2).paragraphs[0].runs[0].text = course
        student_table.cell(1, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(1, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(1, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(1, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(2, 0).paragraphs[0].runs[0].text = student_member_list[1]
        student_table.cell(2, 2).paragraphs[0].runs[0].text = course
        student_table.cell(2, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(2, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(2, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(2, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(3, 0).paragraphs[0].runs[0].text = student_member_list[2]
        student_table.cell(3, 2).paragraphs[0].runs[0].text = course
        student_table.cell(3, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(3, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(3, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(3, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(4, 0).paragraphs[0].runs[0].text = student_member_list[3]
        student_table.cell(4, 2).paragraphs[0].runs[0].text = course
        student_table.cell(4, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(4, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(4, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(4, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(5, 0).paragraphs[0].runs[0].text = student_member_list[4]
        student_table.cell(5, 2).paragraphs[0].runs[0].text = course
        student_table.cell(5, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(5, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(5, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(5, 4).paragraphs[0].runs[0].text = ""

    doc.paragraphs[0].runs[3].text = date_submitted
    doc.paragraphs[1].runs[2].text = panel_full_name

    try:
        doc.paragraphs[8].runs[0].text = research_title_list[0]
    except:
        doc.paragraphs[8].runs[0].text = ""

    try:
        doc.paragraphs[9].runs[0].text = research_title_list[1]
    except:
        doc.paragraphs[9].runs[0].text = ""

    try:
        doc.paragraphs[10].runs[0].text = research_title_list[2]
    except:
        doc.paragraphs[10].runs[0].text = ""

    try:
        doc.paragraphs[11].runs[0].text = research_title_list[3]
    except:
        doc.paragraphs[11].runs[0].text = ""

    try:
        doc.paragraphs[12].runs[0].text = research_title_list[4]
    except:
        doc.paragraphs[12].runs[0].text = ""

    doc.paragraphs[14].runs[1].text = defense_date
    doc.paragraphs[14].runs[4].text = defense_start_time
    doc.paragraphs[14].runs[6].text = defense_end_time
    doc.paragraphs[22].runs[0].text = dit_head_full_name

    panel_table.cell(0, 9).paragraphs[0].runs[0].text = panel_response_date

    if panel_response == "accepted":
        panel_table.cell(0, 1).paragraphs[0].runs[0].text = "✓"
        panel_table.cell(0, 3).paragraphs[0].runs[0].text = "__"

    if panel_response == "declined":
        panel_table.cell(0, 1).paragraphs[0].runs[0].text = "__"
        panel_table.cell(0, 3).paragraphs[0].runs[0].text = "✓"


    if get_panel_invitation.dit_head_signature == 1:
        # Check if DIT Head E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_invitation.dit_head_username) + ".png"):
            head_signature_table.cell(0, 0).text = ''
            head_signature = head_signature_table.cell(0, 0).add_paragraph()
            head_signature_run = head_signature.add_run()
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
        else:
            get_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
            get_accepted_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
            get_pending_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-panel-invitation-dashboard.html", context)

    if get_panel_invitation.panel_signature == True:
        # Check if Panel E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_invitation.panel_username) + ".png"):
            panel_signature_table.cell(0, 0).text = ''
            panel_signature = panel_signature_table.cell(0, 0).add_paragraph()
            panel_signature_run = panel_signature.add_run()
            panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.panel_username +'.png',width=Inches(1.2), height=Inches(0.45))


        else:
            get_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
            get_accepted_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
            get_pending_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-panel-invitation-dashboard.html", context)


    # Create - QR Code
    auth_qr_code = qrcode.make('Topic Panel Invitation\nH:' + dit_head_response_date + '\nP: ' + panel_response_date)
    type(auth_qr_code)  
    auth_qr_code.save(current_user.username + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION-QR.png")

    # INSERT IMAGE
    qr_code = qr_code_box.cell(0, 0).add_paragraph()
    qr_code_run = qr_code.add_run()
    qr_code_run.add_picture(current_user.username + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION-QR.png", width=Inches(1), height=Inches(1))

    doc.save(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx")
    convert(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx")

    filePath = FilePath(
        student_leader_username=current_user.username, 
        file_path=current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf"
        )
    filePath.save()

    os.startfile(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf")

    # doc.save('/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx')
    # subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', "/home/johnanthonybataller/tupc-research-defense-form-django/static/"+current_user.username+"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx', "--outdir" ,"/home/johnanthonybataller/tupc-research-defense-form-django/static/"])
    # download_link = "http://johnanthonybataller.pythonanywhere.com/static/" +current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf'

    # filePath =  FilePath(
    #     student_leader_username = current_user.username,
    #     file_path = '/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf'
    # )
    # filePath.save()

    qr_code_path = current_user.username + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION-QR.png"
    if os.path.isfile(qr_code_path):
        os.remove(qr_code_path)
        print("QR Code has been deleted")
    else:
        print("QR Code does not exist")

    bet3_topic_defense_panel_inviation_docx = current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx"
    # bet3_topic_defense_panel_inviation_docx = ("/home/johnanthonybataller/tupc-research-defense-form-django/static/" + current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx')

    if os.path.isfile(bet3_topic_defense_panel_inviation_docx):
        os.remove(bet3_topic_defense_panel_inviation_docx)
        print("Panel Invitation BET-3 has been deleted")
    else:
        print("Panel Invitation BET-3 does not exist")

    get_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    get_accepted_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
    get_pending_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        #'download_link': download_link,
        "panel_invitations": get_panel_invitations,
        "accepted_panel_invitations": get_accepted_panel_invitations.count(),
        "pending_panel_invitations": get_pending_panel_invitations.count(),
        "response": "sweet downloaded",
    }

    return render(request, "student-bet3-panel-invitation-dashboard.html", context)


# Student - BET3 - Research Title Defense - Download Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentDownloadBET3ResearchTitleDefenseForm(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
        get_panel_chairman = TitleDefenseForm.objects.get(student_leader_username=current_user.username, is_panel_chairman=True)
        print("pass 1")
    except:
        print("pass 1.1")
        return redirect("student-bet3-research-title-defense")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)
    get_panel_members = TitleDefenseForm.objects.all().filter(student_leader_username=current_user.username, is_panel_chairman=False)

    ############## BET-3 RESEARCH TITLE DEFENSE DATA ##############
    date = get_student_leader_data.research_title_defense_date

    try:
        student_1 = get_research_titles[0].student_leader_name
        degree_1 = get_student_leader_data.course_major_abbr
    except:
        student_1 = ""
        degree_1 = ""

    try:
        student_2 = get_group_members[0].student_member_full_name
        degree_2 = get_student_leader_data.course_major_abbr
    except:
        student_2 = ""
        degree_2 = ""

    try:
        student_3 = get_group_members[1].student_member_full_name
        degree_3 = get_student_leader_data.course_major_abbr
    except:
        student_3 = ""
        degree_3 = ""

    try:
        student_4 = get_group_members[2].student_member_full_name
        degree_4 = get_student_leader_data.course_major_abbr
    except:
        student_4 = ""
        degree_4 = ""

    try:
        student_5 = get_group_members[3].student_member_full_name
        degree_5 = get_student_leader_data.course_major_abbr
    except:
        student_5 = ""
        degree_5 = ""

    accepted_title = None
    revise_title = None
    suggested_title = None

    try:
        title_1 = get_research_titles[0].research_title

        if get_research_titles[0].status == "Title Defense - Accepted":
            comment_1 = "Accepted"
            accepted_title = get_research_titles[0].research_title
        elif get_research_titles[0].status == "Title Defense - Revise Title":
            comment_1 = "Revise Title"
            revise_title = get_research_titles[0].research_title
        elif get_research_titles[0].status == "Title Defense - Deferred":
            comment_1 = "Deferred"

    except:
        title_1 = ""
        comment_1 = ""

    try:
        title_2 = get_research_titles[1].research_title

        if get_research_titles[1].status == "Title Defense - Accepted":
            comment_2 = "Accepted"
            accepted_title = get_research_titles[1].research_title
        elif get_research_titles[1].status == "Title Defense - Revise Title":
            comment_2 = "Revise Title"
            revise_title = get_research_titles[1].research_title
        elif get_research_titles[1].status == "Title Defense - Deferred":
            comment_2 = "Deferred"

    except:
        title_2 = ""
        comment_2 = ""

    try:
        title_3 = get_research_titles[2].research_title

        if get_research_titles[2].status == "Title Defense - Accepted":
            comment_3 = "Accepted"
            accepted_title = get_research_titles[2].research_title
        elif get_research_titles[2].status == "Title Defense - Revise Title":
            revise_title = get_research_titles[2].research_title
        elif get_research_titles[2].status == "Title Defense - Deferred":
            comment_3 = "Deferred"

    except:
        title_3 = ""
        comment_3 = ""

    try:
        title_4 = get_research_titles[3].research_title

        if get_research_titles[3].status == "Title Defense - Accepted":
            comment_4 = "Accepted"
            accepted_title = get_research_titles[3].research_title
        elif get_research_titles[3].status == "Title Defense - Revise Title":
            comment_4 = "Revise Title"
            revise_title = get_research_titles[3].research_title
        elif get_research_titles[3].status == "Title Defense - Deferred":
            comment_4 = "Deferred"

    except:
        title_4 = ""
        comment_4 = ""

    try:
        title_5 = get_research_titles[4].research_title

        if get_research_titles[4].status == "Title Defense - Accepted":
            comment_5 = "Accepted"
            accepted_title = get_research_titles[4].research_title
        elif get_research_titles[4].status == "Title Defense - Revise Title":
            comment_5 = "Revise Title"
            revise_title = get_research_titles[4].research_title
        elif get_research_titles[4].status == "Title Defense - Deferred":
            comment_5 = "Deferred"

    except:
        title_5 = ""
        comment_5 = ""

    try:
        if get_research_titles[0].suggested_title != "":
            suggested_title = get_research_titles[0].suggested_title
    except:
        pass

    try:
        if get_research_titles[1].suggested_title != "":
            suggested_title = get_research_titles[1].suggested_title
    except:
        pass

    try:
        if get_research_titles[2].suggested_title != "":
            suggested_title = get_research_titles[2].suggested_title
    except:
        pass

    try:
        if get_research_titles[3].suggested_title != "":
            suggested_title = get_research_titles[3].suggested_title
    except:
        pass

    try:
        if get_research_titles[4].suggested_title != "":
            suggested_title = get_research_titles[4].suggested_title
    except:
        pass

    if not suggested_title:
        suggested_title = "___________________________________"

    panel_chairman = get_panel_chairman.panel_full_name

    try:
        panel_1 = get_panel_members[0].panel_full_name
    except:
        panel_1 = ""

    try:
        panel_2 = get_panel_members[1].panel_full_name
    except:
        panel_2 = ""

    try:
        panel_3 = get_panel_members[2].panel_full_name
    except:
        panel_3 = ""

    try:
        panel_4 = get_panel_members[3].panel_full_name
    except:
        panel_4 = ""

    panel_5 = ""
    panel_6 = ""
    ############## BET-3 RESEARCH TITLE DEFENSE DATA ##############

    doc = Document("static/forms/2-RESEARCH-TITLE-DEFENSE-FORM.docx")
    # doc = Document('/home/johnanthonybataller/tupc-research-defense-form-django/static/forms/2-RESEARCH-TITLE-DEFENSE-FORM.docx')

    doc.paragraphs[0].runs[1].text = date
    print(doc.paragraphs[0].runs[1].text)  # Date of Title defense

    # EXAMINEE
    student_name = doc.tables[0]
    student_name.cell(1, 3).paragraphs[0].runs[0].text = student_1
    student_name.cell(2, 3).paragraphs[0].runs[0].text = student_2
    student_name.cell(3, 3).paragraphs[0].runs[0].text = student_3
    student_name.cell(4, 3).paragraphs[0].runs[0].text = student_4
    student_name.cell(5, 3).paragraphs[0].runs[0].text = student_5
    print(student_name.cell(1, 3).text)
    print(student_name.cell(2, 3).text)
    print(student_name.cell(3, 3).text)
    print(student_name.cell(4, 3).text)
    print(student_name.cell(5, 3).text)
    # column - row

    # STUDENT COURSE
    student_course = doc.tables[0]
    student_course.cell(1, 5).paragraphs[0].runs[0].text = degree_1
    student_course.cell(2, 5).paragraphs[0].runs[0].text = degree_2
    student_course.cell(3, 5).paragraphs[0].runs[0].text = degree_3
    student_course.cell(4, 5).paragraphs[0].runs[0].text = degree_4
    student_course.cell(5, 5).paragraphs[0].runs[0].text = degree_5
    print(student_course.cell(1, 5).text)
    print(student_course.cell(2, 5).text)
    print(student_course.cell(3, 5).text)
    print(student_course.cell(4, 5).text)
    print(student_course.cell(5, 5).text)

    # TITLES
    titles = doc.tables[1]
    titles.cell(1, 1).paragraphs[0].runs[0].text = title_1
    titles.cell(2, 1).paragraphs[0].runs[0].text = title_2
    titles.cell(3, 1).paragraphs[0].runs[0].text = title_3
    titles.cell(4, 1).paragraphs[0].runs[0].text = title_4
    titles.cell(5, 1).paragraphs[0].runs[0].text = title_5
    print(titles.cell(1, 1).text)
    print(titles.cell(2, 1).text)
    print(titles.cell(3, 1).text)
    print(titles.cell(4, 1).text)
    print(titles.cell(5, 1).text)

    # COMMENT
    comment = doc.tables[1]
    comment.cell(1, 2).paragraphs[0].runs[0].text = comment_1
    comment.cell(2, 2).paragraphs[0].runs[0].text = comment_2
    comment.cell(3, 2).paragraphs[0].runs[0].text = comment_3
    comment.cell(4, 2).paragraphs[0].runs[0].text = comment_4
    comment.cell(5, 2).paragraphs[0].runs[0].text = comment_5
    print(comment.cell(1, 2).text)
    print(comment.cell(2, 2).text)
    print(comment.cell(3, 2).text)
    print(comment.cell(4, 2).text)
    print(comment.cell(5, 2).text)

    doc.paragraphs[2].runs[1].text = suggested_title
    print(doc.paragraphs[2].runs[1].text)  # SUGGESTEDTITLE

    panel_chair_signature_table = doc.tables[2]

    doc.paragraphs[8].runs[0].text = panel_chairman
    print(doc.paragraphs[8].runs[0].text)  # PANELCHAIRMAN

    # PANEL SIGNATURE
    panel123 = doc.tables[6]
    panel123.cell(0, 0).paragraphs[0].runs[0].text = panel_1
    panel123.cell(0, 2).paragraphs[0].runs[0].text = panel_2
    panel123.cell(0, 4).paragraphs[0].runs[0].text = panel_3

    panel456 = doc.tables[8]
    panel456.cell(0, 0).paragraphs[0].runs[0].text = panel_4
    # panel456.cell(0, 2).paragraphs[0].runs[0].text = ""
    # panel456.cell(0, 4).paragraphs[0].runs[0].text = ""


    if get_panel_chairman.panel_signature_attach == True:
        # Check if Panel E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_chairman.panel_username) + ".png"):
            panel_chair_signature_table.cell(0, 0).text = ''
            panel_signature = panel_chair_signature_table.cell(0, 0).add_paragraph()
            panel_signature_run = panel_signature.add_run()
            panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_chairman.panel_username +'.png',width=Inches(1.2), height=Inches(0.45))
            panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_chairman.panel_username +'.png',width=Inches(1.2), height=Inches(0.45))

        else:
            context = {
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-research-title-defense.html", context)
    

    # Panel 1 Signature Box
    panel1_sign_box = doc.tables[4]
    print(panel1_sign_box.cell(0, 0).text)

    try:
        panel1_sign = get_panel_members[0].panel_full_name
        print("pass")
        if get_panel_members[0].panel_signature_attach == True:
            print("pass")
            # Check if Panel E-Sign Exist
            if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_members[0].panel_username) + ".png"):
                panel1_sign_box.cell(0, 0).text = ''
                panel_signature = panel1_sign_box.cell(0, 0).add_paragraph()
                panel_signature_run = panel_signature.add_run()
                panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_members[0].panel_username +'.png',width=Inches(1.2), height=Inches(0.45))
            else:
                context = {
                    "response": "sweet faculty member no signature",
                }

                return render(request, "student-bet3-research-title-defense.html", context)
    except:
        print("Live Signature")
        pass

    # Panel 2 Signature Box
    panel2_sign_box = doc.tables[5]
    print(panel1_sign_box.cell(0, 0).text)

    try:
        panel1_sign = get_panel_members[1].panel_full_name
        print("pass")
        if get_panel_members[1].panel_signature_attach == True:
            print("pass")
            # Check if Panel E-Sign Exist
            if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_members[1].panel_username) + ".png"):
                panel2_sign_box.cell(0, 0).text = ''
                panel_signature = panel2_sign_box.cell(0, 0).add_paragraph()
                panel_signature_run = panel_signature.add_run()
                panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_members[1].panel_username +'.png',width=Inches(1.2), height=Inches(0.45))
            else:
                context = {
                    "response": "sweet faculty member no signature",
                }

                return render(request, "student-bet3-research-title-defense.html", context)
    except:
        print("Live Signature")
        pass

    # Panel 3 Signature Box
    panel3_sign_box = doc.tables[3]
    print(panel3_sign_box.cell(0, 0).text)

    try:
        panel1_sign = get_panel_members[2].panel_full_name
        print("pass")
        if get_panel_members[2].panel_signature_attach == True:
            print("pass")
            # Check if Panel E-Sign Exist
            if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_members[2].panel_username) + ".png"):
                panel3_sign_box.cell(0, 0).text = ''
                panel_signature = panel3_sign_box.cell(0, 0).add_paragraph()
                panel_signature_run = panel_signature.add_run()
                panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_members[2].panel_username +'.png',width=Inches(1.2), height=Inches(0.45))
            else:
                context = {
                    "response": "sweet faculty member no signature",
                }

                return render(request, "student-bet3-research-title-defense.html", context)
    except:
        print("Live Signature")
        pass


    # Panel 4 Signature Box
    panel4_sign_box = doc.tables[7]
    print(panel4_sign_box.cell(0, 0).text)

    try:
        panel1_sign = get_panel_members[3].panel_full_name
        print("pass")
        if get_panel_members[3].panel_signature_attach == True:
            print("pass")
            # Check if Panel E-Sign Exist
            if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_members[3].panel_username) + ".png"):
                panel4_sign_box.cell(0, 0).text = ''
                panel_signature = panel4_sign_box.cell(0, 0).add_paragraph()
                panel_signature_run = panel_signature.add_run()
                panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_members[3].panel_username +'.png',width=Inches(1.2), height=Inches(0.45))
            else:
                context = {
                    "response": "sweet faculty member no signature",
                }

                return render(request, "student-bet3-research-title-defense.html", context)
    except:
        print("Live Signature")
        pass

    if accepted_title:
        img = qrcode.make(
            "Research Title Defense"
            + "\n Date & Time of Defense:"
            + get_student_leader_data.research_title_defense_date
            + " "
            + get_student_leader_data.research_title_defense_start_time
            + " to "
            + get_student_leader_data.research_title_defense_end_time
        )
        type(img)
        img.save(current_user.username + "-BET3-TITLE-DEFENSE-QR.png")

    if revise_title:
        img = qrcode.make(
            "Research Title Defense"
            + "\n Date & Time of Defense:"
            + get_student_leader_data.research_title_defense_date
            + " "
            + get_student_leader_data.research_title_defense_start_time
            + " to "
            + get_student_leader_data.research_title_defense_end_time
        )
        type(img)
        img.save(current_user.username + "-BET3-TITLE-DEFENSE-QR.png")

    qr_code_box = doc.tables[9]

    # INSERT IMAGE
    qr_code = qr_code_box.cell(0, 0).add_paragraph()
    qr_code_run = qr_code.add_run()
    qr_code_run.add_picture(current_user.username + "-BET3-TITLE-DEFENSE-QR.png", width=Inches(1), height=Inches(1))
    # INSERT IMAGE

    # SAVE DOCX - COVERT TO PDF
    doc.save(current_user.username + "-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx")
    convert(current_user.username + "-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx")
    # SAVE DOCX - COVERT TO PDF

    filePath = FilePath(student_leader_username=current_user.username, file_path=current_user.username + "-BET3-RESEARCH-TITLE-DEFENSE-FORM.pdf")
    filePath.save()

    os.startfile(current_user.username + "-BET3-RESEARCH-TITLE-DEFENSE-FORM.pdf")

    # UN COMMENT IF DEPLOYED
    # doc.save('/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username + '-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx')
    # subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', "/home/johnanthonybataller/tupc-research-defense-form-django/static/"+current_user.username + '-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx', "--outdir" ,"/home/johnanthonybataller/tupc-research-defense-form-django/static/"])
    # download_link = "http://johnanthonybataller.pythonanywhere.com/static/"+current_user.username + '-BET3-RESEARCH-TITLE-DEFENSE-FORM.pdf'

    # filePath =  FilePath(
    #     student_leader_username = current_user.username,
    #     file_path = '/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username + '-BET3-RESEARCH-TITLE-DEFENSE-FORM.pdf'
    # )
    # filePath.save()
    # UN COMMENT IF DEPLOYED

    qr_code_path = current_user.username + "-BET3-TITLE-DEFENSE-QR.png"
    if os.path.isfile(qr_code_path):
        os.remove(qr_code_path)
        print("BET-3 Research Title Defense QR Code has been deleted")
    else:
        print("BET-3 Research Title Defense QR Code does not exist")

    bet3_research_title_defense_form_docx = current_user.username + "-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx"
    # bet3_research_title_defense_form_docx = ("/home/johnanthonybataller/tupc-research-defense-form-django/static/" + current_user.username + '-BET3-RESEARCH-TITLE-DEFENSE-FORM.docx')

    if os.path.isfile(bet3_research_title_defense_form_docx):
        os.remove(bet3_research_title_defense_form_docx)
        print("BET-3 Research Title Defense Form has been deleted")
    else:
        print("BET-3 Research Title Defense Form does not exist")

    # Get Student Group Members
    try:
        get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    except:
        get_student_group_members = None

    # Get Student Research Title / Titles
    try:
        get_student_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)
    except:
        print("pass research titles")
        return redirect("student-dashboard")

    # Get Student Accepted Research Title
    try:
        get_student_accepted_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, status="Title Defense - Accepted")
    except:
        get_student_accepted_research_title = None

    # Get Student Accepted - Revise Title Research Title
    try:
        get_student_revise_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, status="Title Defense - Revise Title")
    except:
        get_student_revise_research_title = None

    # Get Panel Research Title Defense Form
    try:
        get_panel_research_title_defense_form = TitleDefenseForm.objects.all().filter(student_leader_username=current_user.username)
    except:
        print("pass research title defense form")
        return redirect("student-dashboard")

    if get_student_leader_data.group_members_status != "completed" and get_student_leader_data.research_titles_status != "completed" and get_student_leader_data.bet3_panel_invitation_status != "completed":
        return redirect("student-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "student_group_members": get_student_group_members,
        "student_research_titles": get_student_research_titles,
        "student_accepted_research_title": get_student_accepted_research_title,
        "student_revise_research_title": get_student_revise_research_title,
        "panel_research_title_defense_form": get_panel_research_title_defense_form,
        #'download_link': download_link,
        "response": "sweet downloaded",
    }

    return render(request, "student-bet3-research-title-defense.html", context)


# Student - BET3 - Research Title Defense - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ResearchTitleDefense(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)

    if get_student_leader_data.bet3_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete bet3 panel invitation"}

        return render(request, "student-bet3-panel-invitation-dashboard.html", context)

    if get_student_leader_data.title_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete title defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    # Get Student Group Members
    try:
        get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    except:
        get_student_group_members = None

    # Get Student Research Title / Titles
    try:
        get_student_research_titles = ResearchTitle.objects.all().filter(student_leader_username=current_user.username)
    except:
        print("pass research titles")
        return redirect("student-dashboard")

    # Get Student Accepted Research Title
    try:
        get_student_accepted_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, status="Title Defense - Accepted")
    except:
        get_student_accepted_research_title = None

    # Get Student Accepted - Revise Title Research Title
    try:
        get_student_revise_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, status="Title Defense - Revise Title")
    except:
        get_student_revise_research_title = None

    # Get Panel Research Title Defense Form
    try:
        get_panel_research_title_defense_form = TitleDefenseForm.objects.all().filter(student_leader_username=current_user.username)
    except:
        print("pass research title defense form")
        return redirect("student-dashboard")

    if get_student_leader_data.group_members_status != "completed" and get_student_leader_data.research_titles_status != "completed" and get_student_leader_data.bet3_panel_invitation_status != "completed":
        return redirect("student-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "student_group_members": get_student_group_members,
        "student_research_titles": get_student_research_titles,
        "student_accepted_research_title": get_student_accepted_research_title,
        "student_revise_research_title": get_student_revise_research_title,
        "panel_research_title_defense_form": get_panel_research_title_defense_form,
    }

    return render(request, "student-bet3-research-title-defense.html", context)


# Student - BET3 - Adviser - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3AdviserDashboard(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)

    if get_student_leader_data.bet3_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete bet3 panel invitation"}

        return render(request, "student-bet3-panel-invitation-dashboard.html", context)

    if get_student_leader_data.title_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete title defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    get_advisers = User.objects.all().filter(is_adviser=1)

    # Student = Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username)
    except:
        check_adviser_conforme = None

    if request.method == "POST":
        adviser_username = request.POST.get("adviser_username")
        form_date_submitted = date_today

        student_leader_username = current_user.username
        student_leader_name = currently_loggedin_user_full_name

        research_title = ""

        # Student = Check Adviser Conforme
        try:
            check_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username)

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "advisers": get_advisers, "adviser_conforme_data": check_adviser_conforme, "response": "sweet adviser conforme exist"}

            return render(request, "student-bet3-adviser-dashboard.html", context)
        except:
            pass

        # Student = Get Accepted Research Title
        try:
            get_accepted_title = ResearchTitle.objects.get(student_leader_username=current_user.username, title_defense_status="Accepted")
            research_title = get_accepted_title.research_title
        except:
            pass

        # Student = Get Revise Research Title
        try:
            get_revise_title = ResearchTitle.objects.get(student_leader_username=current_user.username, title_defense_status="Revise Title")
            research_title = get_revise_title.research_title
        except:
            pass
        # DIT Head - Get DIT Head Data
        try:
            get_dit_head_data = User.objects.get(is_department_head=1)

            dit_head_username = get_dit_head_data.username

            dit_head_name = fullNameProcess(request, dit_head_username)

        except:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "advisers": get_advisers, "response": "sweet DIT Head unassigned"}

            return render(request, "student-bet3-adviser-dashboard.html", context)

        # Adviser - Get Adviser Data
        try:
            get_adviser_data = User.objects.get(username=adviser_username, is_adviser=1)

            adviser_username = get_adviser_data.username

            adviser_name = fullNameProcess(request, adviser_username)
        except:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "advisers": get_advisers, "response": "sweet Adviser not found"}

            return render(request, "student-bet3-adviser-dashboard.html", context)

        #  Adviser - If Advisee Count Reached
        if get_adviser_data.advisee_count == get_adviser_data.advisee_limit:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "advisers": get_advisers, "response": "sweet Advisee limit count reached"}

            return render(request, "student-bet3-adviser-dashboard.html", context)

        print("Research Title:", research_title)

        # Student Leader Full Name
        if get_student_leader_data.middle_name == "":
            student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
        else:
            student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

        save_adviser_conforme = AdviserConforme(
            student_leader_username=current_user.username,
            student_leader_full_name=student_leader_full_name,
            course=get_student_leader_data.course_major_abbr,
            research_title=research_title,
            form_date_submitted=date_today,
            dit_head_username=get_dit_head_data.username,
            dit_head_name=dit_head_name,
            dit_head_response="Pending",
            adviser_username=get_adviser_data.username,
            adviser_name=adviser_name,
            adviser_response="On hold",
        )
        save_adviser_conforme.save()

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "advisers": get_advisers, "adviser_name": adviser_name, "response": "sweet adviser conforme sent"}

        return render(request, "student-bet3-adviser-dashboard.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "adviser_conforme_data": check_adviser_conforme,
        "advisers": get_advisers,
    }

    return render(request, "student-bet3-adviser-dashboard.html", context)


# Student - BET-3 Adviser Conforme - Download
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3AdviserConformeDownload(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("logout_user")

    # BET-3 - Get Adviser Conforme
    try:
        get_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username, form_status="Accepted")
    except:
        return redirect("student-bet3-adviser-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    try:
        student_1 = student_leader_full_name
        course_1 = get_student_leader_data.course.replace("Engineering", "Eng.")
        major_1 = get_student_leader_data.major
    except:
        student_1 = ""
        course_1 = ""
        major_1 = ""

    try:
        student_2 = get_group_members[0].student_member_full_name
        course_2 = get_student_leader_data.course.replace("Engineering", "Eng.")
        major_2 = get_student_leader_data.major
    except:
        student_2 = ""
        course_2 = ""
        major_2 = ""

    try:
        student_3 = get_group_members[1].student_member_full_name
        course_3 = get_student_leader_data.course.replace("Engineering", "Eng.")
        major_3 = get_student_leader_data.major
    except:
        student_3 = ""
        course_3 = ""
        major_3 = ""

    try:
        student_4 = get_group_members[2].student_member_full_name
        course_4 = get_student_leader_data.course.replace("Engineering", "Eng.")
        major_4 = get_student_leader_data.major
    except:
        student_4 = ""
        course_4 = ""
        major_4 = ""

    try:
        student_5 = get_group_members[3].student_member_full_name
        course_5 = get_student_leader_data.course.replace("Engineering", "Eng.")
        major_5 = get_student_leader_data.major
    except:
        student_5 = ""
        course_5 = ""
        major_5 = ""

    course_major = get_student_leader_data.course + " Major in " + get_student_leader_data.major
    research_title = get_adviser_conforme.research_title
    date_submitted = get_adviser_conforme.form_date_submitted

    dit_head_name = get_adviser_conforme.dit_head_name

    adviser_name = get_adviser_conforme.adviser_name
    adviser_response_date = get_adviser_conforme.adviser_response_date

    doc = Document("static/forms/3-RESEARCH-ADVISER-CONFORME.docx")
    # doc = Document('/home/johnanthonybataller/tupc-research-defense-form-django/static/forms/3-RESEARCH-ADVISER-CONFORME')

    doc.paragraphs[0].runs[3].text = date_submitted

    doc.paragraphs[1].runs[2].text = adviser_name

    # doc.paragraphs[6].runs[1].text = adviser_name

    # STUDENTS NAME
    student_table = doc.tables[0]

    student_table.cell(1, 0).paragraphs[0].runs[0].text = student_1
    student_table.cell(2, 0).paragraphs[0].runs[0].text = student_2
    student_table.cell(3, 0).paragraphs[0].runs[0].text = student_3
    student_table.cell(4, 0).paragraphs[0].runs[0].text = student_4
    student_table.cell(5, 0).paragraphs[0].runs[0].text = student_5

    # student_table.cell(1, 2).paragraphs[0].runs[0].text = course
    # student_table.cell(1, 4).paragraphs[0].runs[0].text = major

    # STUDENT COURSE
    student_table.cell(1, 1).paragraphs[0].runs[0].text = course_1
    student_table.cell(2, 1).paragraphs[0].runs[0].text = course_2
    student_table.cell(3, 1).paragraphs[0].runs[0].text = course_3
    student_table.cell(4, 1).paragraphs[0].runs[0].text = course_4
    student_table.cell(5, 1).paragraphs[0].runs[0].text = course_5

    # STUDENT MAJOR

    student_table.cell(1, 2).paragraphs[0].runs[0].text = major_1
    student_table.cell(2, 2).paragraphs[0].runs[0].text = major_2
    student_table.cell(3, 2).paragraphs[0].runs[0].text = major_3
    student_table.cell(4, 2).paragraphs[0].runs[0].text = major_4
    student_table.cell(5, 2).paragraphs[0].runs[0].text = major_5

    doc.paragraphs[8].runs[1].text = research_title

    doc.paragraphs[22].runs[0].text = dit_head_name

    doc.paragraphs[30].runs[0].text = adviser_name
    doc.paragraphs[33].runs[0].text = adviser_response_date

    head_signature_table = doc.tables[1]
    adviser_signature_table = doc.tables[3]

    if get_adviser_conforme.dit_head_signature == 1:
        # Check if DIT Head E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_adviser_conforme.dit_head_username) + ".png"):
            head_signature_table.cell(0, 0).text = ''
            head_signature = head_signature_table.cell(0, 0).add_paragraph()
            head_signature_run = head_signature.add_run()
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_adviser_conforme.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_adviser_conforme.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
        else:
            get_advisers = User.objects.all().filter(is_adviser=1)

            # Student = Check Adviser Conforme
            try:
                check_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username)
            except:
                check_adviser_conforme = None

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    "student_leader_data": get_student_leader_data,
                    "advisers": get_advisers,
                    "adviser_conforme_data": check_adviser_conforme,
                    #'download_link': download_link,
                    "response": "sweet faculty member no signature",
                }

                return render(request, "student-bet3-adviser-dashboard.html", context)

    if get_adviser_conforme.adviser_signature == 1:
        print("Adviser attach esign")
        # Check if DIT Head E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_adviser_conforme.adviser_username) + ".png"):
            print("Adviser esign found")
            adviser_signature_table.cell(0, 0).text = ''
            adviser_signature = adviser_signature_table.cell(0, 0).add_paragraph()
            adviser_signature_run = adviser_signature.add_run()
            adviser_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_adviser_conforme.adviser_username +'.png',width=Inches(1.2), height=Inches(0.45))
        else:
            print("Not Found")
            get_advisers = User.objects.all().filter(is_adviser=1)

            # Student = Check Adviser Conforme
            try:
                check_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username)
            except:
                check_adviser_conforme = None

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "advisers": get_advisers,
                "adviser_conforme_data": check_adviser_conforme,
                #'download_link': download_link,
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-adviser-dashboard.html", context)

    img = qrcode.make("Research Adviser Conforme: " + "\n H: " + get_adviser_conforme.dit_head_response_date + "\n A: " + get_adviser_conforme.adviser_response_date)
    type(img)
    img.save(current_user.username + "-BET3-ADVISER-CONFORME.png")

    qr_code_box = doc.tables[2]

    # INSERT IMAGE
    qr_code = qr_code_box.cell(0, 0).add_paragraph()
    qr_code_run = qr_code.add_run()
    qr_code_run.add_picture(current_user.username + "-BET3-ADVISER-CONFORME.png", width=Inches(1), height=Inches(1))
    # INSERT IMAGE

    # SAVE DOCX - COVERT TO PDF
    doc.save(current_user.username + "-BET3-ADVISER-CONFORME.docx")
    convert(current_user.username + "-BET3-ADVISER-CONFORME.docx")
    # SAVE DOCX - COVERT TO PDF

    os.startfile(current_user.username + "-BET3-ADVISER-CONFORME.pdf")

    filePath = FilePath(student_leader_username=current_user.username, file_path=current_user.username + "-BET3-ADVISER-CONFORME.pdf")
    filePath.save()

    # UN COMMENT IF DEPLOYED
    # doc.save('/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +'-BET3-ADVISER-CONFORME.docx')
    # subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', "/home/johnanthonybataller/tupc-research-defense-form-django/static/"+current_user.username +'-BET3-ADVISER-CONFORME.docx', "--outdir" ,"/home/johnanthonybataller/tupc-research-defense-form-django/static/"])
    # download_link = "http://johnanthonybataller.pythonanywhere.com/static/"+current_user.username +'-BET3-ADVISER-CONFORME.pdf'

    # filePath =  FilePath(
    #     student_leader_username = current_user.username,
    #     file_path = '/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +'-BET3-ADVISER-CONFORME.pdf'
    # )
    # filePath.save()
    # UN COMMENT IF DEPLOYED

    qr_code_path = current_user.username + "-BET3-ADVISER-CONFORME.png"
    if os.path.isfile(qr_code_path):
        os.remove(qr_code_path)
        print("BET-3 Adviser Conforme QR Code has been deleted")
    else:
        print("BET-3 Adviser Conforme QR Code does not exist")

    bet3_adviser_conforme_docx = current_user.username + "-BET3-ADVISER-CONFORME.docx"
    # bet3_adviser_conforme_docx = ("/home/johnanthonybataller/tupc-research-defense-form-django/static/" + current_user.username +'-BET3-ADVISER-CONFORME.pdf')

    if os.path.isfile(bet3_adviser_conforme_docx):
        os.remove(bet3_adviser_conforme_docx)
        print("BET-3 Adviser Conforme has been deleted")
    else:
        print("BET-3 Adviser Conforme does not exist")

    # Student = Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(student_leader_username=current_user.username)
    except:
        check_adviser_conforme = None

    get_advisers = User.objects.all().filter(is_adviser=1)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "advisers": get_advisers,
        "adviser_conforme_data": check_adviser_conforme,
        #'download_link': download_link,
        "response": "sweet downloaded",
    }

    return render(request, "student-bet3-adviser-dashboard.html", context)

##### STUDENT - PROPOSAL DEFENSE #####

# Student - BET3 - Proposal Defense - Panel Invitation
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitation(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)
    ############## PAGE VALIDATION ##############

    get_topic_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)

    get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
    get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")


    get_topic_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    previous_panel_count = get_topic_panel_invitations.count()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "panel_invitations": get_panel_invitations,
        "accepted_panel_invitations": get_accepted_panel_invitations.count(),
        "pending_panel_invitations": get_pending_panel_invitations.count(),
        "previous_panel": get_topic_panel_invitations,
    }

    return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)


# Student - BET3 - Proposal Defense - Panel Invitation - Create for previous Panel Members
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitationCreatePanel(request):
    current_user = request.user
    current_password = current_user.password

     # Student Leader - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)

    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status == "completed":
        return redirect("student-bet3-proposal-defense-panel-invitation-dashboard")
    ############## PAGE VALIDATION ##############

    # Topic Defense - Panel Invitation - Get Previous Panel Members
    get_previous_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, panel_attendance = "present")
    previous_panel_member_count = get_previous_panel_members.count()

    # Proposal  Defense - Panel Invitation - Get Previous Panel Members
    get_proposal_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status = "pending")
    proposal_defense_count = get_proposal_panel_invitations.count()

    # Users - Get all Panel Members
    panel_members = User.objects.all().filter(is_panel=1)

    # Defense Schedule - Get all Proposal Defense Schedule
    defense_dates = DefenseSchedule.objects.all().filter(course=get_student_leader_data.course_major_abbr, username=get_student_leader_data.bet3_subject_teacher_username, form="Research Proposal Defense", status="Available")

    # If Student has no Research Proposal Defense Schedule
    if get_student_leader_data.research_proposal_defense_date != "":
        pass
    else:
        if not defense_dates:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "response": "sweet no defense schedule"}

            return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
        else:
            pass

    # Department Head - Check if there is a DIT Head assigned
    try:
        dept_head = User.objects.get(is_department_head=1)

        if dept_head.middle_name == "":
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.last_name + " " + dept_head.suffix
        else:
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.middle_name[0] + " " + dept_head.last_name + " " + dept_head.suffix
    except:
        print("No Department Head")

        context = {"response": "sweet no DIT Head"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-create-panel.html", context)


    defense_date_list = []
    for defense_date_id in defense_dates:
        defense_date_list.append(defense_date_id.id)

    # Student Leader - Get Full Name
    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if int(get_student_leader_data.request_limit) == int(proposal_defense_count):
        print("Count:",proposal_defense_count)
        print("Request Limit Exceed")

        get_topic_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)

        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")


        get_topic_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        previous_panel_count = get_topic_panel_invitations.count()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "currently_loggedin_user_account": currently_loggedin_user_account,
            "student_leader_data": get_student_leader_data,
            "panel_invitations": get_panel_invitations,
            "accepted_panel_invitations": get_accepted_panel_invitations.count(),
            "pending_panel_invitations": get_pending_panel_invitations.count(),
            "previous_panel": get_topic_panel_invitations,

             "response": "sweet request limit exceed"
        }

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    if request.method == "POST":
        defense_schedule_input = request.POST.get("defense_schedule_input")

        # Topic Defense - Panel Invitation - Get Previous Panel Members
        get_previous_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=current_user.username, panel_attendance = "present")
        previous_panel_member_count = get_previous_panel_members.count()
        
        # Defense Schedule - Check if input date is valid
        if int(defense_schedule_input) not in defense_date_list:

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,

                "student_leader_data": get_student_leader_data,

                "dept_head_name": dept_head_name,

                "panel_members": panel_members,

                "defense_dates": defense_dates,

                "previous_panel": get_previous_panel_members,

                "response": "sweet invalid defense schedule"
                }

            print("Student - Proposal Defense Schedule - Invalid")
            return render(request, "student-bet3-proposal-defense-panel-invitation-create-panel.html", context)

        else:

            # Defense Schedule - Save Proposal Defense Schedule
            try:
                save_defense_schedule = DefenseSchedule.objects.get(id=int(defense_schedule_input))

                save_defense_schedule.student_leader_username = current_user.username
                save_defense_schedule.student_leader_name = student_leader_full_name
                save_defense_schedule.status = "Reserved"
                save_defense_schedule.save()

                print("Student - Defense Schedule - Proposal Defense Schedule - Reserved")

            except:
                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "student_leader_data": get_student_leader_data, 
                    "dept_head_name": dept_head_name, 
                    "panel_members": panel_members, 
                    "defense_dates": defense_dates, 
                    "response": "sweet defense schedule not found"}

                print("Student - Proposal Defense Schedule - Not Found")
                return render(request, "student-proposal-defense-panel-invitation-create-panel.html", context)

            # Student Leader - Update Proposal Defense Schedule
            get_student_leader_data.research_proposal_defense_date = save_defense_schedule.date
            get_student_leader_data.research_proposal_defense_start_time = save_defense_schedule.start_time
            get_student_leader_data.research_proposal_defense_end_time = save_defense_schedule.end_time
            get_student_leader_data.request_limit = 5
            get_student_leader_data.save()
            print("Student - Student Leader -  Proposal Defense Schedule - Updated")

            for i in range(len(get_previous_panel_members)):
                send_proposal_defense_panel_invitation = ProposalPanelInvitation(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name,
                    course_major_abbr=get_student_leader_data.course_major_abbr,

                    dit_head_username=dept_head.username,
                    dit_head_full_name=dept_head_name,
                    dit_head_response="pending",

                    panel_username=get_previous_panel_members[i].panel_username,
                    panel_full_name=get_previous_panel_members[i].panel_full_name,
                    panel_response="on hold",

                    research_proposal_defense_date=save_defense_schedule.date,
                    research_proposal_defense_start_time=save_defense_schedule.start_time,
                    research_proposal_defense_end_time=save_defense_schedule.end_time,

                    form_status="pending",
                    form_date_sent=today.strftime("%B %d, %Y"),
                    form="Proposal Defense Panel Invitation",

                    subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                    subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
                    
                )
                send_proposal_defense_panel_invitation.save()
                i + 1
            

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account,

            "student_leader_data": get_student_leader_data,

            "dept_head_name": dept_head_name, 
            "panel_members": panel_members, 
            "defense_dates": defense_dates,

            "previous_panel": get_previous_panel_members,

            "response": "sweet panel invitation sent"}
            
        print("Student -  Proposal Defense Panel Invitation - Previous Panel Members - Sent")
        return render(request, "student-bet3-proposal-defense-panel-invitation-create-panel.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "dept_head_name": dept_head_name,
        "panel_members": panel_members,
        "defense_dates": defense_dates,

        "previous_panel": get_previous_panel_members,
    }

    return render(request, "student-bet3-proposal-defense-panel-invitation-create-panel.html", context)


# Student - BET3 - Proposal Defense - Panel Invitation - Create Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitationCreate(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "response": "sweet incomplete group members"}

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "response": "sweet incomplete research titles"}

        return render(request, "student-add-research-title.html", context)

    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status == "completed":
        return redirect("student-bet3-proposal-defense-panel-invitation")
    ############## PAGE VALIDATION ##############

    try:
        get_pending_panel_invitation = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")
        pending_count = get_pending_panel_invitation.count()

        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

        if int(get_student_leader_data.request_limit) == int(pending_count):
            print(get_student_leader_data.request_limit)
            print(int(pending_count))
            print("Request Limit Exceed")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet request limit exceed"
            }

            return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    except:
        pass

    
    try:
        get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        accepted_count = get_accepted_panel_invitations.count()

        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
       
        get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

        if int(5) == int(accepted_count):
            print(get_student_leader_data.request_limit)
            print(int(accepted_count))
            print("Request Limit Exceed")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet request limit exceed"
            }

            return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    except:
        pass

    panel_members = User.objects.all().filter(is_panel=1)

    defense_dates = DefenseSchedule.objects.all().filter(course=get_student_leader_data.course_major_abbr, username=get_student_leader_data.bet3_subject_teacher_username, status="Available")

    if get_student_leader_data.research_proposal_defense_date != "":
        pass
    else:
        if not defense_dates:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "response": "sweet no defense schedule"
                }

            return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
        else:
            pass

    defense_date_list = []

    panel_list = []

    # Check if there is DIT Head assigned.
    try:
        dept_head = User.objects.get(is_department_head=1)

        if dept_head.middle_name == "":
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.last_name + " " + dept_head.suffix
        else:
            dept_head_name = dept_head.honorific + " " + dept_head.first_name + " " + dept_head.middle_name[0] + " " + dept_head.last_name + " " + dept_head.suffix

    except:
        print("No Department Head")

        context = {"response": "sweet no DIT Head"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)

    # Check if there is a Panel assigned.
    if not panel_members or panel_members.count() < 5:
        print("Incomplete Faculty Member")

        context = {"response": "sweet inc panel"}
        return render(request, "student-bet3-proposal-defense-panel-invitation-create.htm", context)
    else:
        for panel in panel_members:
            panel_list.append(panel.username)

    for defense_date_id in defense_dates:
        defense_date_list.append(defense_date_id.id)

    student_leader_full_name = None

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if request.method == "POST":
        defense_schedule_input = request.POST.get("defense_schedule_input")
        panel_input = request.POST.get("panel_input")

        # Check if the entered Panel is valid
        if panel_input not in panel_list:

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "response": "sweet invalid panel"}

            return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)

        # Check if there are Panel Members assigned
        try:
            get_panel_data = User.objects.get(username=panel_input)

            if get_panel_data.middle_name == "":
                panel_full_name = get_panel_data.honorific + " " + get_panel_data.first_name + " " + get_panel_data.last_name + " " + get_panel_data.suffix
            else:
                panel_full_name = get_panel_data.honorific + " " + get_panel_data.first_name + " " + get_panel_data.middle_name[0] + " " + get_panel_data.last_name + " " + get_panel_data.suffix

        except:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "response": "sweet panel not found"}

            return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)

        # Check if the entered Panel Member is Subject Teacher
        try:
            StudentLeader.objects.get(username=current_user.username, bet3_subject_teacher_username=panel_input)

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "panel_full_name": panel_full_name, 
                "response": "sweet subject teacher"}

            return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Pending Panel Invitation
        try:
            ProposalPanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "panel_full_name": panel_full_name, 
                "response": "sweet panel invitation exist"}

            return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Accepted Panel Invitation
        try:
            ProposalPanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="accepted")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "panel_full_name": panel_full_name,
                "response": "sweet panel invitation accepted exist"
                }

            return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)
        except:
            pass

        try:
            check_defense_schedule = DefenseSchedule.objects.get(student_leader_username=current_user.username, form="Research Proposal Defense")
            print(check_defense_schedule)
            send_panel_invitation = ProposalPanelInvitation(
                student_leader_username=current_user.username,
                student_leader_full_name=student_leader_full_name,
                course_major_abbr=get_student_leader_data.course_major_abbr,
                dit_head_username=dept_head.username,
                dit_head_full_name=dept_head_name,
                dit_head_response="pending",
                panel_username=get_panel_data.username,
                panel_full_name=panel_full_name,
                panel_response="on hold",
                research_proposal_defense_date=check_defense_schedule.date,
                research_proposal_defense_start_time=check_defense_schedule.start_time,
                research_proposal_defense_end_time=check_defense_schedule.end_time,
                form_status="pending",
                form_date_sent=date_today,
                form="Proposal Defense Panel Invitation",
                subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
            )
            send_panel_invitation.save()
            print("Panel Invitation Sent")

        except:
            # Check if the entered Defense Scheduled is valid
            if str(defense_schedule_input) not in defense_date_list:

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "dept_head_name": dept_head_name, 
                    "panel_members": panel_members, 
                    "defense_dates": defense_dates, 
                    "response": "sweet invalid defense schedule"
                    }

                return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)
            else:

                # Save Defense Schedule Table
                try:
                    save_defense_schedule = DefenseSchedule.objects.get(id=int(defense_schedule_input))

                    save_defense_schedule.student_leader_username = current_user.username
                    save_defense_schedule.student_leader_name = student_leader_full_name
                    save_defense_schedule.status = "Reserved"
                    save_defense_schedule.save()
                    print("Defense Schedule Data Updated")

                except:
                    context = {
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                        "currently_loggedin_user_account": currently_loggedin_user_account, 
                        "student_leader_data": get_student_leader_data, 
                        "dept_head_name": dept_head_name, 
                        "panel_members": panel_members, 
                        "defense_dates": defense_dates, 
                        "response": "sweet defense schedule not found"
                        }

                    return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)

                get_student_leader_data.research_title_defense_date = save_defense_schedule.date
                get_student_leader_data.research_title_defense_start_time = save_defense_schedule.start_time
                get_student_leader_data.research_title_defense_end_time = save_defense_schedule.end_time
                get_student_leader_data.save()
                print("Student Leader Data Updated")

                send_panel_invitation = ProposalPanelInvitation(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                    dit_head_username=dept_head.username,
                    dit_head_full_name=dept_head_name,
                    dit_head_response="pending",
                    panel_username=get_panel_data.username,
                    panel_full_name=panel_full_name,
                    panel_response="on hold",
                    research_proposal_defense_date=save_defense_schedule.date,
                    research_proposal_defense_start_time=save_defense_schedule.start_time,
                    research_proposal_defense_end_time=save_defense_schedule.end_time,
                    form_status="pending",
                    form_date_sent=today.strftime("%B %d, %Y"),
                    form="Proposal Defense Panel Invitation",
                    subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                    subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
                )
                send_panel_invitation.save()
                print("Panel Invitation Sent")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "student_leader_data": get_student_leader_data, 
            "dept_head_name": dept_head_name, 
            "panel_members": panel_members, 
            "defense_dates": defense_dates, 
            "response": "sweet panel invitation sent"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "dept_head_name": dept_head_name,
        "panel_members": panel_members,
        "defense_dates": defense_dates,
    }

    return render(request, "student-bet3-proposal-defense-panel-invitation-create.html", context)


# Student - BET3 - Proposal Defense - Panel Invitation - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitationSave(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    ############## PAGE VALIDATION ##############
    if get_student_leader_data.group_members_status != "completed":
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            
            "response": "sweet incomplete group members"
            }

        return render(request, "student-add-group-member.html", context)

    if get_student_leader_data.research_titles_status != "completed":
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "response": "sweet incomplete research titles"
            }

        return render(request, "student-add-research-title.html", context)
    ############## PAGE VALIDATION ##############

    get_student_leader_data.bet3_proposal_defense_panel_invitation_status = "completed"
    get_student_leader_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "response": "sweet bet-3 panel invitation saved"}

    return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)


# Student - BET3 - Proposal Defense - Panel Invitation - Download Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitationDownload(request, id):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
        get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
        get_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, title_defense_status = "Accepted")
        get_panel_invitation = ProposalPanelInvitation.objects.get(id=int(id), student_leader_username=current_user.username)

    except:
        return redirect("student-bet3-proposal-defense-panel-invitation-dashboard")

    ############## BET-3 PANEL INVITATION DATA ##############
    date_submitted = get_panel_invitation.form_date_sent

    student_member_list = [get_panel_invitation.student_leader_full_name]
    course = get_student_leader_data.course.replace("Engineering", "Eng.")
    major = get_student_leader_data.major


    defense_date = get_panel_invitation.research_proposal_defense_date
    defense_start_time = get_panel_invitation.research_proposal_defense_start_time
    defense_end_time = get_panel_invitation.research_proposal_defense_end_time

    dit_head_full_name = get_panel_invitation.dit_head_full_name
    dit_head_response = get_panel_invitation.dit_head_response
    dit_head_response_date = get_panel_invitation.dit_head_response_date

    panel_full_name = get_panel_invitation.panel_full_name
    panel_username = get_panel_invitation.panel_username
    panel_response = get_panel_invitation.panel_response
    panel_response_date = get_panel_invitation.panel_response_date
    ############## BET-3 PANEL INVITATION DATA ##############

    if get_group_members:
        for group_member in get_group_members:
            student_member_list.append(group_member.student_member_full_name)

    student_member_list.sort()

    print("Date Sent: ", date_submitted)

    print("Group Members: ", student_member_list)
    print("Course: ", course)
    print("Major: ", major)
    print("Research Title: ", get_research_title.research_title)

    print("Defense Date: ", defense_date)
    print("Defense Start Time: ", defense_start_time)
    print("Defense End Time: ", defense_end_time)

    print("DIT Head Name: ", dit_head_full_name)
    print("DIT Head Response: ", dit_head_response)
    print("DIT Head Response Date: ", dit_head_response_date)

    print("Panel Name: ", panel_full_name)
    print("Panel Response: ", panel_response)
    print("Panel Response Date: ", panel_response_date)

    doc = Document("static/forms/4-PROPOSAL-DEFENSE-PANEL-INVITATION.docx")
    # doc = Document('/home/johnanthonybataller/tupc-research-defense-form-django/static/forms/1-TOPIC-DEFENSE-PANEL-INVITATION.docx')

    student_table = doc.tables[0] # Student Data Table
    head_signature_table = doc.tables[1]
    panel_table = doc.tables[2] # Panel Data Table
    qr_code_box = doc.tables[4]
    panel_signature_box = doc.tables[3]

    try:
        student_table.cell(1, 0).paragraphs[0].runs[0].text = student_member_list[0]
        student_table.cell(1, 2).paragraphs[0].runs[0].text = course
        student_table.cell(1, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(1, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(1, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(1, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(2, 0).paragraphs[0].runs[0].text = student_member_list[1]
        student_table.cell(2, 2).paragraphs[0].runs[0].text = course
        student_table.cell(2, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(2, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(2, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(2, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(3, 0).paragraphs[0].runs[0].text = student_member_list[2]
        student_table.cell(3, 2).paragraphs[0].runs[0].text = course
        student_table.cell(3, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(3, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(3, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(3, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(4, 0).paragraphs[0].runs[0].text = student_member_list[3]
        student_table.cell(4, 2).paragraphs[0].runs[0].text = course
        student_table.cell(4, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(4, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(4, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(4, 4).paragraphs[0].runs[0].text = ""

    try:
        student_table.cell(5, 0).paragraphs[0].runs[0].text = student_member_list[4]
        student_table.cell(5, 2).paragraphs[0].runs[0].text = course
        student_table.cell(5, 4).paragraphs[0].runs[0].text = major
    except:
        student_table.cell(5, 0).paragraphs[0].runs[0].text = ""
        student_table.cell(5, 2).paragraphs[0].runs[0].text = ""
        student_table.cell(5, 4).paragraphs[0].runs[0].text = ""

    doc.paragraphs[0].runs[2].text = date_submitted
    doc.paragraphs[1].runs[1].text = panel_full_name

    doc.paragraphs[4].runs[6].text = get_research_title.research_title

    doc.paragraphs[6].runs[1].text = defense_date
    doc.paragraphs[6].runs[3].text = defense_start_time
    doc.paragraphs[6].runs[5].text = defense_end_time
    doc.paragraphs[17].runs[0].text = dit_head_full_name

    panel_table.cell(0, 9).paragraphs[0].runs[0].text = panel_response_date

    if panel_response == "accepted":
        panel_table.cell(0, 1).paragraphs[0].runs[0].text = "✓"
        panel_table.cell(0, 3).paragraphs[0].runs[0].text = "__"

    if panel_response == "declined":
        panel_table.cell(0, 1).paragraphs[0].runs[0].text = "__"
        panel_table.cell(0, 3).paragraphs[0].runs[0].text = "✓"


    if get_panel_invitation.dit_head_signature == 1:
        # Check if DIT Head E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_invitation.dit_head_username) + ".png"):
            head_signature_table.cell(0, 0).text = ''
            head_signature = head_signature_table.cell(0, 0).add_paragraph()
            head_signature_run = head_signature.add_run()
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
            head_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.dit_head_username +'.png',width=Inches(1.2), height=Inches(0.45))
        else:
            get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
            get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
            get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-proposal-defense-panel-invitation.html", context)

    if get_panel_invitation.panel_signature == True:
        # Check if Panel E-Sign Exist
        if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(get_panel_invitation.panel_username) + ".png"):
            panel_signature_box.cell(0, 0).text = ''
            panel_signature = panel_signature_box.cell(0, 0).add_paragraph()
            panel_signature_run = panel_signature.add_run()
            panel_signature_run.add_picture('uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'+get_panel_invitation.panel_username +'.png',width=Inches(1.2), height=Inches(0.45))


        else:
            get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
            get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
            get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "student_leader_data": get_student_leader_data,
                "panel_invitations": get_panel_invitations,
                "accepted_panel_invitations": get_accepted_panel_invitations.count(),
                "pending_panel_invitations": get_pending_panel_invitations.count(),
                "response": "sweet faculty member no signature",
            }

            return render(request, "student-bet3-proposal-defense-panel-invitation.html", context)


    # Create - QR Code
    auth_qr_code = qrcode.make('Proposal Defense Panel Invitation\nH:' + dit_head_response_date + '\nP: ' + panel_response_date)
    type(auth_qr_code)  
    auth_qr_code.save(current_user.username + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION-QR.png")

    # INSERT IMAGE
    qr_code = qr_code_box.cell(0, 0).add_paragraph()
    qr_code_run = qr_code.add_run()
    qr_code_run.add_picture(current_user.username + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION-QR.png", width=Inches(1), height=Inches(1))

    doc.save(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.docx")
    convert(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.docx")

    filePath = FilePath(
        student_leader_username=current_user.username, 
        file_path=current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.pdf"
        )
    filePath.save()

    os.startfile(current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.pdf")

    # doc.save('/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx')
    # subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', "/home/johnanthonybataller/tupc-research-defense-form-django/static/"+current_user.username+"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.docx', "--outdir" ,"/home/johnanthonybataller/tupc-research-defense-form-django/static/"])
    # download_link = "http://johnanthonybataller.pythonanywhere.com/static/" +current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf'

    # filePath =  FilePath(
    #     student_leader_username = current_user.username,
    #     file_path = '/home/johnanthonybataller/tupc-research-defense-form-django/static/'+current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-TOPIC-DEFENSE-PANEL-INVITATION.pdf'
    # )
    # filePath.save()

    qr_code_path = current_user.username + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION-QR.png"
    if os.path.isfile(qr_code_path):
        os.remove(qr_code_path)
        print("QR Code has been deleted")
    else:
        print("QR Code does not exist")

    bet3_proposal_defense_panel_inviation_docx = current_user.username + "-" + panel_username + "-" + panel_response + "-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.docx"
    # bet3_proposal_defense_panel_inviation_docx = ("/home/johnanthonybataller/tupc-research-defense-form-django/static/" + current_user.username +"-"+panel_username+"-"+panel_response+'-BET3-PROPOSAL-DEFENSE-PANEL-INVITATION.docx')

    if os.path.isfile(bet3_proposal_defense_panel_inviation_docx):
        os.remove(bet3_proposal_defense_panel_inviation_docx)
        print("Panel Invitation BET-3 has been deleted")
    else:
        print("Panel Invitation BET-3 does not exist")

    get_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    get_accepted_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
    get_pending_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        #'download_link': download_link,
        "panel_invitations": get_panel_invitations,
        "accepted_panel_invitations": get_accepted_panel_invitations.count(),
        "pending_panel_invitations": get_pending_panel_invitations.count(),
        "response": "sweet downloaded",
    }

    return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)


# Student - Panel Conforme BET-3 Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelConformeBet3(request):
    current_user = request.user

    try:
        PanelConformeBET3.objects.get(student_leader_username=current_user)
        print("Panel Conforme - BET-3 Exist")
        return redirect("student-panel-conforme-bet3-form")

    except:
        panel_members = User.objects.all().filter(is_panel=1)

        try:
            dept_head_check = User.objects.get(is_department_head=1)
            pass
        except:
            print("No DIT Head")
            context = {"response": "sweet inc form"}

            return render(request, "student-panel-conforme-bet-3-create.html", context)

        if not panel_members or panel_members.count() < 5:
            print("Incomplete Faculty Member")
            context = {"response": "sweet inc form"}

            return render(request, "student-panel-conforme-bet-3-create.html", context)
        else:
            pass

        print("Panel Conforme - BET-3 Create")
        return redirect("student-panel-conforme-bet3-create")


# Student - Panel Conforme BET-3 Create Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelConformeBet3Create(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
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
        research_title_input = request.POST.get("research_title_input")
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
        panel1_input = request.POST.get("panel1_input")
        print("Panel 1 =", panel1_input)

        # Get Panel Member 2 Name
        panel2_input = request.POST.get("panel2_input")
        print("Panel 2 =", panel2_input)

        # Get Panel Member 3 Name
        panel3_input = request.POST.get("panel3_input")
        print("Panel 3 =", panel3_input)

        # Get Panel Member 4 Name
        panel4_input = request.POST.get("panel4_input")
        print("Panel 4 =", panel4_input)

        # Get Panel Member 5 Name
        panel5_input = request.POST.get("panel5_input")
        print("Panel 5 =", panel5_input)

        # Get Student member 1 Username
        student1_username_input = current_user.username
        print("Student Username 1 =", student1_username_input)

        # Get Student Member 2 Name
        student2_input = request.POST.get("student2_input")
        print("Student 2 =", student2_input)

        # Get Student member 2 Username
        student2_username_input = request.POST.get("student2_username_input")
        print("Student Username 2 =", student2_username_input)

        # Get Student Member 3 Name
        student3_input = request.POST.get("student3_input")
        print("Student 3 =", student3_input)

        # Get Student member 3 Username
        student3_username_input = request.POST.get("student3_username_input")
        print("Student Username 3 =", student3_username_input)

        # Get Student Member 4 Name
        student4_input = request.POST.get("student4_input")
        print("Student 4 =", student4_input)

        # Get Student member 4 Username
        student4_username_input = request.POST.get("student4_username_input")
        print("Student Useranme 4 =", student4_username_input)

        # Get Student Member 5 Name
        student5_input = request.POST.get("student5_input")
        print("Student 5 =", student5_input)

        # Get Student member 5 Username
        student5_username_input = request.POST.get("student5_username_input")
        print("Student Username 5 =", student5_username_input)

        # Check if Student Member 2 has an account
        try:
            student_username_check = User.objects.get(username=student2_username_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "username_exist": student2_username_input, "response": "sweet student member exist 2"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")
        except:
            pass

        # Check if Student Member 3 has an account
        try:
            student_username_check = User.objects.get(username=student3_username_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "username_exist": student3_username_input, "response": "sweet student member exist 3"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")
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
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username invalid"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")

            # If Student ID No. is the same with the others
            if student1_username_input == student4_username_input or student2_username_input == student4_username_input or student3_username_input == student4_username_input or student4_username_input == student1_username_input or student4_username_input == student2_username_input or student4_username_input == student3_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username same"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")

            # Check if Student Member 4 has an account
            try:
                student_username_check = User.objects.get(username=student4_username_input)

                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "username_exist": student4_username_input, "response": "sweet student member exist 4"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")
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
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username invalid"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")

            # If Student ID No. is the same with the others
            if student1_username_input == student5_username_input or student2_username_input == student5_username_input or student3_username_input == student5_username_input or student4_username_input == student5_username_input or student5_username_input == student1_username_input or student5_username_input == student2_username_input or student5_username_input == student3_username_input or student5_username_input == student4_username_input:
                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username same"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")

            # Check if Student Member 5 has an account
            try:
                student_username_check = User.objects.get(username=student5_username_input)

                try:
                    dept_head_check = User.objects.get(is_department_head=1)
                    dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                    panel_check = User.objects.filter(is_panel=1)

                    course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                    course_name = course_check.course
                    major_name = course_check.major

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "username_exist": student5_username_input, "response": "sweet student member exist 5"}

                    return render(request, "student-panel-conforme-bet-3-create.html", context)

                except:
                    return redirect("student-dashboard")
            except:
                pass

        # If the Student already has a Panel Conform BET-3
        try:
            PanelConformeBET3.objects.get(student_leader_username=current_user.username)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "panel conforme bet-3 exist"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        except:
            pass

        #  If Research Title is existing
        try:
            ResearchTitle.objects.get(research_title=research_title_input)

            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "existing research title"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        except:
            pass

        # If Panel Input is Default
        if panel1_input == "default" or panel2_input == "default" or panel3_input == "default" or panel4_input == "default" or panel5_input == "default":
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "choose 5 panel"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        # If Panel Name input is the same with the other Panel Name Input
        if (
            panel1_input == panel2_input
            or panel1_input == panel3_input
            or panel1_input == panel4_input
            or panel1_input == panel5_input
            or panel2_input == panel1_input
            or panel2_input == panel3_input
            or panel2_input == panel4_input
            or panel2_input == panel5_input
            or panel3_input == panel1_input
            or panel3_input == panel2_input
            or panel3_input == panel4_input
            or panel3_input == panel5_input
            or panel4_input == panel1_input
            or panel4_input == panel2_input
            or panel4_input == panel3_input
            or panel4_input == panel5_input
            or panel5_input == panel1_input
            or panel5_input == panel2_input
            or panel5_input == panel3_input
            or panel5_input == panel4_input
        ):
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "same panel"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        # If Panel Name input is not in the Panel Member List
        if panel1_input not in panel_member_check_list or panel2_input not in panel_member_check_list or panel3_input not in panel_member_check_list or panel4_input not in panel_member_check_list or panel5_input not in panel_member_check_list:
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "sweet panel not in the list"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        # If Student ID No. is invalid
        if "TUPC" not in student1_username_input or "TUPC" not in student2_username_input or "TUPC" not in student3_username_input:
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username invalid"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

        # If Student ID No. is the same with the others
        if student1_username_input == student2_username_input or student1_username_input == student3_username_input or student2_username_input == student1_username_input or student2_username_input == student3_username_input or student3_username_input == student1_username_input or student3_username_input == student2_username_input:
            try:
                dept_head_check = User.objects.get(is_department_head=1)
                dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

                panel_check = User.objects.filter(is_panel=1)

                course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
                course_name = course_check.course
                major_name = course_check.major

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel_check": panel_check, "leader_member_name": leader_member_name_2, "leader_member_username": current_user.username, "course_name": course_name, "major_name": major_name, "response": "username same"}

                return render(request, "student-panel-conforme-bet-3-create.html", context)

            except:
                return redirect("student-dashboard")

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
            student_leader_username=current_user,
            dept_head=dept_head_name_input,
            dept_head_status="pending",
            panel_member_1=panel1_input,
            panel_member_2=panel2_input,
            panel_member_3=panel3_input,
            panel_member_4=panel4_input,
            panel_member_5=panel5_input,
            panel_member_name_1=panel_member_full_name_1,
            panel_member_name_2=panel_member_full_name_2,
            panel_member_name_3=panel_member_full_name_3,
            panel_member_name_4=panel_member_full_name_4,
            panel_member_name_5=panel_member_full_name_5,
            panel_member_status_1="waiting for DIT Head",
            panel_member_status_2="waiting for DIT Head",
            panel_member_status_3="waiting for DIT Head",
            panel_member_status_4="waiting for DIT Head",
            panel_member_status_5="waiting for DIT Head",
            student_member_1=student1_input,
            student_member_2=student2_input,
            student_member_3=student3_input,
            student_member_4=student4_input,
            student_member_5=student5_input,
            student_member_username_1=student1_username_input,
            student_member_username_2=student2_username_input,
            student_member_username_3=student3_username_input,
            student_member_username_4=student4_username_input,
            student_member_username_5=student5_username_input,
            course=course_abbr,
            major=major_input,
            course_major_abbr=user_course,
            research_title=research_title_input.title(),
            date_submitted=date_today,
            form_status="Pending",
        )

        panel_conforme_form.save()

        research_title_form = ResearchTitle(
            research_title=research_title_input.title(),
            course_major_abbr=user_course,
            course=course_name,
            major=major_input,
            student_leader_username=current_user.username,
            student_leader_name=leader_member_name_2,
            status="ongoing",
            date_submitted=date_today,
        )

        research_title_form.save()

        student_member_group_2 = StudentGroupMember(
            student_leader_username=current_user.username,
            student_leader_name=leader_member_name_2,
            student_member_username=student2_username_input,
            student_member_name=student2_input,
            course=course_name,
            major=major_input,
            course_major_abbr=user_course,
        )

        student_member_group_2.save()

        student_member_group_3 = StudentGroupMember(
            student_leader_username=current_user.username,
            student_leader_name=leader_member_name_2,
            student_member_username=student3_username_input,
            student_member_name=student3_input,
            course=course_name,
            major=major_input,
            course_major_abbr=user_course,
        )

        student_member_group_3.save()

        if student4_input:
            student_member_group_4 = StudentGroupMember(
                student_leader_username=current_user.username,
                student_leader_name=leader_member_name_2,
                student_member_username=student4_username_input,
                student_member_name=student4_input,
                course=course_name,
                major=major_input,
                course_major_abbr=user_course,
            )

            student_member_group_4.save()

        if student5_input:
            student_member_group_5 = StudentGroupMember(
                student_leader_username=current_user.username,
                student_leader_name=leader_member_name_2,
                student_member_username=student5_username_input,
                student_member_name=student5_input,
                course=course_name,
                major=major_input,
                course_major_abbr=user_course,
            )

            student_member_group_5.save()

        return redirect("student-dashboard")

    try:
        dept_head_check = User.objects.get(is_department_head=1)
        dept_head_name = None

        panel_check = User.objects.filter(is_panel=1)

        if dept_head_check.middle_name == "":
            dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_check.last_name

        else:
            dept_head_middle_initial = dept_head_check.middle_name[0]
            dept_head_name = dept_head_check.honorific + " " + dept_head_check.first_name + " " + dept_head_middle_initial + ". " + dept_head_check.last_name

        course_check = StudentCourseMajor.objects.get(course_major_abbr=user_course)
        course_name = course_check.course
        major_name = course_check.major

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "currently_loggedin_user_account": currently_loggedin_user_account,
            "dept_head_name": dept_head_name,
            "panel_members": panel_members,
            "panel_check": panel_check,
            "leader_member_name": leader_member_name_2,
            "leader_member_username": current_user.username,
            "course_name": course_name,
            "major_name": major_name,
        }
        return render(request, "student-panel-conforme-bet-3-create.html", context)

    except:
        print("Incomplete Form")
        context = {"user_full_name": user_full_name}
        return render(request, "student-panel-conforme-bet-3-create.html", context)


# Student - Panel Conforme BET-3 Form Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentPanelConformeBet3Form(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
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
        return redirect("student-dashboard")

    # Generate PDF Form
    if request.method == "POST":
        print("Download PDF")
        doc = Document("static/forms/2-PANEL-CONFORME.docx")

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

        print(doc.paragraphs[1].runs[1].text)  # Date Today 1
        print(doc.paragraphs[3].runs[0].text)  # Receiver 1
        print(doc.paragraphs[6].runs[1].text)  # Receiver 2
        print(doc.paragraphs[7].runs[1].text)  # Subject
        print(doc.paragraphs[7].runs[4].text)  # Student Course
        print(doc.paragraphs[7].runs[6].text)  # Student Major
        print(doc.paragraphs[10].runs[1].text)  # Research Title
        print(doc.paragraphs[15].runs[0].text)  # Department Head Name

        doc.paragraphs[1].runs[1].text = date_submitted
        doc.paragraphs[3].runs[0].text = "Mr. Jay Victor Gumboc"
        doc.paragraphs[6].runs[1].text = "Mr. Jay Victor Gumboc"
        doc.paragraphs[7].runs[1].text = "BET-3"
        doc.paragraphs[7].runs[4].text = "Bachelor of Engineering Technology"
        doc.paragraphs[7].runs[6].text = "Major in Computer Engienering Technology"
        doc.paragraphs[10].runs[1].text = research_title
        doc.paragraphs[15].runs[0].text = dept_head_name

        # INSERT IMAGE
        # qr_code = qr_code_table.cell(0, 0).add_paragraph()
        # qr_code_run = qr_code.add_run()
        # qr_code_run.add_picture('qr-code.png',width=Inches(0.8), height=Inches(0.8))
        # qr_code_run.alignment=WD_ALIGN_PARAGRAPH.CENTER

        doc.save("2-PANEL-CONFROME-BET-3-{}.docx".format(current_user))
        convert("2-PANEL-CONFROME-BET-3-{}.docx".format(current_user))
        os.startfile("2-PANEL-CONFROME-BET-3-{}.pdf".format(current_user))

        doc.save("2-PANEL-CONFORME-NEW.docx")
        convert("2-PANEL-CONFORME-NEW.docx")
        os.startfile("2-PANEL-CONFORME-NEW.pdf")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "dept_head_name": dept_head_name, "panel1": panel1, "panel2": panel2, "panel3": panel3, "panel4": panel4, "panel5": panel5, "student1": student1, "student2": student2, "student3": student3, "student4": student4, "student5": student5, "course": course, "major": major, "research_title": research_title, "form_status": form_status}
        return render(request, "student-panel-conforme-bet-3-form.html", context)

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "dept_head_name": dept_head_name, "panel1": panel1, "panel2": panel2, "panel3": panel3, "panel4": panel4, "panel5": panel5, "student1": student1, "student2": student2, "student3": student3, "student4": student4, "student5": student5, "course": course, "major": major, "research_title": research_title, "form_status": form_status}

    return render(request, "student-panel-conforme-bet-3-form.html", context)


# Student - BET-3 Panel Invitation - Logs
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3PanelInvitationLogs(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    get_panel_invitations_logs = TitlePanelInvitationLog.objects.all().filter(student_leader_username=current_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "panel_invitations": get_panel_invitations_logs,
    }

    return render(request, "student-bet3-panel-invitation-logs.html", context)

# Student - BET-3 - Propsoal Defense - Panel Invitation - Logs
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalDefensePanelInvitationLogs(request):
    current_user = request.user
    current_password = current_user.password

    ############## TOPBAR ##############
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]
    ############## TOPBAR ##############

    # Student - Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=current_user.username)
    except:
        return redirect("index")

    get_panel_invitations_logs = ProposalPanelInvitationLog.objects.all().filter(student_leader_username=current_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "panel_invitations": get_panel_invitations_logs,
    }

    return render(request, "student-bet3-proposal-defense-panel-invitation-logs.html", context)

##########################################################################################################################


# Admin - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminDashboard(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account}

    return render(request, "admin-dashboard.html", context)


# Admin - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminProfile(request):
    current_user = request.user
    current_password = request.user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Admin Profile
    current_username = request.user.username

    user_first_name = current_user.first_name
    user_middle_name = current_user.middle_name
    user_last_name = current_user.last_name
    user_email = current_user.email

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "user_first_name": user_first_name,
        "user_middle_name": user_middle_name,
        "user_last_name": user_last_name,
        "username": current_username,
        "user_email": user_email,
    }

    if request.method == "POST":
        current_password_input = request.POST.get("current_password_input")
        new_password_input = request.POST.get("new_password_input")
        confirm_new_password_input = request.POST.get("confirm_new_password_input")

        if current_password_input == current_password:

            if current_password_input != new_password_input:

                if new_password_input == confirm_new_password_input:

                    User.objects.filter(username=current_user).update(password=new_password_input)

                    context = {"response": "changed password"}
                    return render(request, "index.html", context)

                else:
                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "username": current_username, "user_email": user_email, "response": "new password and confirm new password doesnt match"}

                    return render(request, "admin-profile.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "username": current_username, "user_email": user_email, "response": "current password and new password is same"}

                return render(request, "admin-profile.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "user_first_name": user_first_name, "user_middle_name": user_middle_name, "user_last_name": user_last_name, "username": current_username, "user_email": user_email, "response": "current password is incorrect"}

            return render(request, "admin-profile.html", context)

    return render(request, "admin-profile.html", context)


# Admin - Student Course and Major Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminStudentCourseMajor(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    all_course_major = StudentCourseMajor.objects.all()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "all_course_major": all_course_major,
    }

    return render(request, "admin-student-course-major.html", context)


# Admin - Student Add Course and Major Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminStudentAddCourseMajor(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        major_input = request.POST.get("major_input")
        course_abbr_input = request.POST.get("course_abbr_input")

        print(course_input)

        if StudentCourseMajor.objects.filter(major=major_input).exists():
            print("Major doesn't exist")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "response": "major exist",
            }

            return render(request, "admin-student-add-course-major.html", context)

        elif StudentCourseMajor.objects.filter(course_major_abbr=course_abbr_input).exists():
            print("Course Abbreviation doesn't exist")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "response": "course abbr exist",
            }

            return render(request, "admin-student-add-course-major.html", context)

        else:
            print("save")
            queryForm = StudentCourseMajor(course=course_input.title(), major=major_input.title(), course_major_abbr=course_abbr_input.upper())
            queryForm.save()

            all_course_major = StudentCourseMajor.objects.all()

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "all_course_major": all_course_major,
                "response": "sweet course added",
            }

            return render(request, "admin-student-course-major.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
    }

    return render(request, "admin-student-add-course-major.html", context)


# Admin - Student Edit Course and Major Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminStudentEditCourseMajor(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        course_major_check = StudentCourseMajor.objects.get(id=id)
    except:
        return redirect("admin-student-course-major")

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        major_input = request.POST.get("major_input")
        course_abbr_input = request.POST.get("course_abbr_input")

        print(course_input)

        if major_input == course_major_check.major:
            print("Major - Pass")
            pass

        else:
            if StudentCourseMajor.objects.filter(major=major_input).exists():
                print("Major - Exist")

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "course_major_check": course_major_check,
                    "response": "sweet major exist",
                }

                return render(request, "admin-student-course-major.html", context)

        if course_abbr_input == course_major_check.course_major_abbr:
            print("Abbr - Pass")
            pass

        else:

            if StudentCourseMajor.objects.filter(course_major_abbr=course_abbr_input).exists():
                print("Abbr - Exist")

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    "course_major_check": course_major_check,
                    "response": "sweet course abbr exist",
                }

                return render(request, "admin-student-course-major.html", context)

        print("save")

        course_major_check.course = course_input.title()
        course_major_check.major = major_input.title()
        course_major_check.course_major_abbr = course_abbr_input.upper()

        course_major_check.save()

        course_major_check_new = StudentCourseMajor.objects.get(id=id)

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "currently_loggedin_user_account": currently_loggedin_user_account,
            "course_major_check": course_major_check_new,
            "response": "sweet course updated",
        }

        return render(request, "admin-student-course-major.html", context)

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "course_major_check": course_major_check}

    return render(request, "admin-student-edit-course-major.html", context)


# Admin - Student Delete Course and Major Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminStudentDeleteCourseMajor(request, id):

    delete_course = StudentCourseMajor.objects.filter(id=id)
    print(delete_course)

    if not delete_course:
        context = {"response": "sweet course not found"}

        return render(request, "admin-student-course-major.html", context)

    else:
        delete_course.delete()

        context = {"response": "sweet course deleted"}

        return render(request, "admin-student-course-major.html", context)


# Admin - Department Head Account Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminFacultyMemberAcc(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
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
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "members": members,
        # 'dept_head_username': dept_head_username,
        # 'dept_head_email': dept_head_email,
        # 'dept_head_first_name': dept_head_first_name,
        # 'dept_head_last_name': dept_head_last_name,
        # 'dept_head_department': dept_head_department,
    }

    return render(request, "admin-faculty-member-account.html", context)


# Admin - Faculty Member Create Account Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminFacultyMemberCreateAcc(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
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
        suffix_list = ["", "Sr.", "Jr.", "I", "II", "III", "IV", "V"]
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", "Library", "Research & Extension"]

        honorific_input = request.POST.get("honorific_input")
        first_name_input = request.POST.get("first_name_input")
        middle_name_input = request.POST.get("middle_name_input")
        last_name_input = request.POST.get("last_name_input")
        suffix_input = request.POST.get("suffix_input")
        user_account_input = request.POST.get("user_account_input")
        form = SignUpForm(request.POST)
        confirm_password = request.POST.get("confirm_password_input")

        print("Create Account Form")
        print("Honorofic Input: ", honorific_input)
        print("First Name: ", first_name_input)
        print("Midle Name: ", middle_name_input)
        print("Last Name: ", last_name_input)
        print("User Account: ", user_account_input)
        print("Confirm Password: ", confirm_password)

        # Form Validation Start

        if honorific_input == "Default":
            print("Choose Honorific")
            print(dit_head_exist)

            context = {
                # Topbar Start
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "choose honorific",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

        if honorific_input not in honorific_list:
            print("Honorific not in list")
            print(dit_head_exist)

            context = {
                # Topbar
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "honorific not in list",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

        if suffix_input not in suffix_list:
            print("Suffix not in list")

            context = {
                # Topbar
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "sweet invalid suffix",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

        if user_account_input == "Default":
            print("Choose User Account")
            print(dit_head_exist)

            context = {
                # Topbar Start
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "choose user account",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

        if user_account_input not in user_account_list:
            print("User Account not in list")
            print(dit_head_exist)

            context = {
                # Topbar Start
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "user account not in list",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

        if user_account_input == "DIT Head":
            try:
                User.objects.get(is_department_head=1)
                print("DIT Head Account Exist")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    # Form
                    "form": form,
                    "dit_head_exist": dit_head_exist,
                }
                return render(request, "admin-faculty-member-create-acc.html", context)

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
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    # Form
                    "form": form,
                    "dit_head_exist": dit_head_exist,
                    # Response
                    "response": "invalid username",
                }

                return render(request, "admin-faculty-member-create-acc.html", context)

            if "@gsfe.tupcavite.edu.ph" not in email_input:
                print("Invalid Email")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    # Form
                    "form": form,
                    "dit_head_exist": dit_head_exist,
                    # Response
                    "response": "invalid email",
                }

                return render(request, "admin-faculty-member-create-acc.html", context)

            if user.password == confirm_password:
                print("valid password")
                user.save()

                if user_account_input == "DIT Head":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.suffix = suffix_input
                    user_check.department = "DIT Head"
                    user_check.is_department_head = 1
                    user_check.is_panel = 1
                    user_check.is_adviser = 1
                    user_check.is_subject_teacher = 1
                    user_check.is_faculty_member = 1
                    user_check.advisee_limit = 5
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        # Response
                        "response": "account created",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

                if user_account_input == "Faculty Member":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.suffix = suffix_input
                    user_check.department = "Faculty Member"
                    user_check.is_panel = 1
                    user_check.is_adviser = 1
                    user_check.is_subject_teacher = 1
                    user_check.is_faculty_member = 1
                    user_check.advisee_limit = 5
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        # Response
                        "response": "account created",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

                if user_account_input == "Academic Affairs":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.suffix = suffix_input
                    user_check.department = "Academic Affairs"
                    user_check.is_academic_affairs = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        # Response
                        "response": "account created",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

                if user_account_input == "Library":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.suffix = suffix_input
                    user_check.department = "Library"
                    user_check.is_library = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        # Response
                        "response": "account created",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

                if user_account_input == "Research & Extension":
                    user_check = User.objects.get(username=user.username)

                    user_check.honorific = honorific_input
                    user_check.first_name = first_name_input.title()
                    user_check.middle_name = middle_name_input.title()
                    user_check.last_name = last_name_input.title()
                    user_check.suffix = suffix_input
                    user_check.department = "Research & Extension"
                    user_check.is_research_extension = 1
                    user_check.is_faculty_member = 1
                    user_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    context = {
                        # Topbar Start
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        # Response
                        "response": "account created",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

            else:
                print("password mismatch")
                print(dit_head_exist)

                context = {
                    # Topbar Start
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    # Form
                    "form": form,
                    "dit_head_exist": dit_head_exist,
                    # Response
                    "response": "password mismatch",
                }

                return render(request, "admin-faculty-member-create-acc.html", context)

        else:
            print("User Exist")
            print(dit_head_exist)

            context = {
                # Topbar Start
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                # Form
                "form": form,
                "dit_head_exist": dit_head_exist,
                # Response
                "response": "username or email exist",
            }

            return render(request, "admin-faculty-member-create-acc.html", context)

    context = {
        # Topbar Start
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        # Form
        "form": form,
        "dit_head_exist": dit_head_exist,
    }
    return render(request, "admin-faculty-member-create-acc.html", context)


# Admin - Faculty Member Individual Account Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminFacultyMemberData(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        member_check = User.objects.get(username=id)
    except:
        return redirect("admin-faculty-member-acc")

    print(member_check.username)
    member_honorific = member_check.honorific
    member_username = member_check.username
    member_email = member_check.email
    member_first_name = member_check.first_name
    member_middle_name = member_check.middle_name
    member_last_name = member_check.last_name
    member_suffix = member_check.suffix
    member_department = member_check.department

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "member_honorific": member_honorific,
        "member_username": member_username,
        "member_email": member_email,
        "member_first_name": member_first_name,
        "member_middle_name": member_middle_name,
        "member_last_name": member_last_name,
        "member_suffix": member_suffix,
        "member_department": member_department,
    }

    if request.method == "POST":
        honorific_list = ["Mr.", "Ms.", "Mrs.", "Engr.", "Dr.", "Dra."]
        suffix_list = ["", "Sr.", "Jr.", "I", "II", "III", "IV", "V"]
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", "Library", "Research & Extension"]

        username_input = request.POST.get("username_input")
        email_input = request.POST.get("email_input")
        honorific_input = request.POST.get("honorific_input")
        first_name_input = request.POST.get("first_name_input")
        middle_name_input = request.POST.get("middle_name_input")
        last_name_input = request.POST.get("last_name_input")
        suffix_input = request.POST.get("suffix_input")
        password_input = request.POST.get("password_input")

        if honorific_input not in honorific_list:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "member_honorific": member_honorific, "member_username": member_username, "member_email": member_email, "member_first_name": member_first_name, "member_middle_name": member_middle_name, "member_last_name": member_last_name, "member_department": member_department, "response": "choose honorific"}

            return render(request, "admin-faculty-member-data.html", context)

        if suffix_input not in suffix_list:
            print("Suffix not in list")

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "member_honorific": member_honorific, "member_username": member_username, "member_email": member_email, "member_first_name": member_first_name, "member_middle_name": member_middle_name, "member_last_name": member_last_name, "member_department": member_department, "response": "sweet invalid suffix"}

            return render(request, "admin-faculty-member-data.html", context)

        if "TUPC" in username_input:
            pass

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "member_honorific": member_honorific, "member_username": member_username, "member_email": member_email, "member_first_name": member_first_name, "member_middle_name": member_middle_name, "member_last_name": member_last_name, "member_department": member_department, "response": "invalid username"}

            return render(request, "admin-faculty-member-data.html", context)

        if "gsfe.tupcavite.edu.ph" in email_input:
            pass

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "member_honorific": member_honorific, "member_username": member_username, "member_email": member_email, "member_first_name": member_first_name, "member_middle_name": member_middle_name, "member_last_name": member_last_name, "member_department": member_department, "response": "invalid email"}

            return render(request, "admin-faculty-member-data.html", context)

        if member_check.password == password_input:

            member_check.honorific = honorific_input
            member_check.first_name = first_name_input.title()
            member_check.middle_name = middle_name_input.title()
            member_check.last_name = last_name_input.title()
            member_check.suffix = suffix_input
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

                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet profile updated"}

                return render(request, "admin-faculty-member-account.html", context)

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

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet partial update username exist"}

                    return render(request, "admin-faculty-member-account.html", context)

                except:
                    member_check.username = username_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=username_input)

                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name

                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet profile updated"}

                    return render(request, "admin-faculty-member-account.html", context)

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

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet partial update email exist"}

                    return render(request, "admin-faculty-member-account.html", context)

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

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet profile updated"}

                    return render(request, "admin-faculty-member-account.html", context)

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

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet partial update username and email exist"}

                    return render(request, "admin-faculty-member-account.html", context)

                except:
                    member_check.username = username_input
                    member_check.email = email_input
                    member_check.save()

                    members = User.objects.all().filter(is_faculty_member=1)

                    sweet_member_check = User.objects.get(username=username_input)

                    sweet_member_username = sweet_member_check.username
                    sweet_member_full_name = None

                    if sweet_member_check.middle_name == "":
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name

                    else:
                        sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet profile updated"}

                    return render(request, "admin-faculty-member-account.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "member_honorific": member_honorific, "member_username": member_username, "member_email": member_email, "member_first_name": member_first_name, "member_middle_name": member_middle_name, "member_last_name": member_last_name, "member_suffix": member_suffix, "member_department": member_department, "response": "incorrect password"}

            return render(request, "admin-faculty-member-data.html", context)

    return render(request, "admin-faculty-member-data.html", context)


# Admin - Faculty Member Change Password Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminFacultyMemberChangePassword(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    faculty_member_check = User.objects.get(username=id)
    current_password = faculty_member_check.password

    if request.method == "POST":
        current_password_input = request.POST.get("current_password_input")
        new_password_input = request.POST.get("new_password_input")
        confirm_new_password_input = request.POST.get("confirm_new_password_input")

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "response": "sweet password changed success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "response": "sweet confirm change password mismatch",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    "members": members,
                    "sweet_member_username": sweet_member_username,
                    "sweet_member_full_name": sweet_member_full_name,
                    "response": "sweet same change password",
                }

                return render(request, "admin-faculty-member-account.html", context)

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
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "members": members,
                "sweet_member_username": sweet_member_username,
                "sweet_member_full_name": sweet_member_full_name,
                "response": "sweet incorrect change current password",
            }

            return render(request, "admin-faculty-member-account.html", context)

    return render(request, "student-profile.html", context)


# Admin - Faculty Member Change User Account Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_administrator, login_url="index")
def adminFacultyMemberChangeUserAccount(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        member_check = User.objects.get(username=id)

    except:
        return redirect("admin-faculty-member-acc")

    print(member_check.department)

    if request.method == "POST":
        user_account_list = ["DIT Head", "Faculty Member", "Academic Affairs", "Library", "Research & Extension"]

        user_account_input = request.POST.get("user_account_input")
        current_password_input = request.POST.get("current_password_input")

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

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet choose user account"}

            return render(request, "admin-faculty-member-account.html", context)

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

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "members": members, "sweet_member_username": sweet_member_username, "sweet_member_full_name": sweet_member_full_name, "response": "sweet user account not in list"}

            return render(request, "admin-faculty-member-account.html", context)

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
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    "members": members,
                    "sweet_member_username": sweet_member_username,
                    "sweet_member_full_name": sweet_member_full_name,
                    "sweet_member_department": sweet_member_department,
                    "response": "sweet already",
                }

                return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "sweet_member_department": user_account_input,
                        "response": "sweet success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "sweet_member_department": user_account_input,
                        "response": "sweet success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "sweet_member_department": user_account_input,
                        "response": "sweet success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "sweet_member_department": user_account_input,
                        "response": "sweet success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                        "currently_loggedin_user_account": currently_loggedin_user_account,
                        "members": members,
                        "sweet_member_username": sweet_member_username,
                        "sweet_member_full_name": sweet_member_full_name,
                        "sweet_member_department": user_account_input,
                        "response": "sweet success",
                    }

                    return render(request, "admin-faculty-member-account.html", context)

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
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "members": members,
                "sweet_member_username": sweet_member_username,
                "sweet_member_full_name": sweet_member_full_name,
                "response": "sweet incorrect current password",
            }

            return render(request, "admin-faculty-member-account.html", context)


##########################################################################################################################

# DIT Head - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {"currently_loggedin_user_data": currently_loggedin_user, "currently_loggedin_user_full_name": currently_loggedin_user_full_name, "date_today": date_today}

    return render(request, "dit-head-dashboard.html", context)


# DIT Head - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadProfile(request):
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

    return render(request, "dit-head-profile.html", context)


# DIT Head - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadCreateESignature(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

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

        return redirect("dit-head-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
    }

    return render(request, "dit-head-signature-pad.html", context)


# Panel - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadUploadESignature(request):
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

                    # Invalid - Delete E-Signature
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

                    return render(request, "dit-head-profile.html", context)
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

                    return render(request, "dit-head-profile.html", context)

                return redirect("dit-head-profile")

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

            return render(request, "dit-head-profile.html", context)


# DIT Head - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("dit-head-profile")


# DIT Head - Acount Settings - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadAccountSettings(request):
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

                    return render(request, "dit-head-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "dit-head-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "dit-head-account-settings.html", context)

    return render(request, "dit-head-account-settings.html", context)


# DIT Head - BET3 - Topic - Panel Invitation
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelInvitationBet3(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        esignature_exist = "True"
        print("E-sign exist")

    else:
        esignature_exist = "False"
        print("E-sign doesn't exist.")

    # PANEL INVITATION BET-3
    get_panel_invitation = TitlePanelInvitation.objects.all().filter(dit_head_response="pending")

    if request.method == "POST":
        requestID = request.POST.get("requestID")
        signature_url = request.POST.get("signature_link")

        print(requestID)

        if signature_url:
            print(requestID)
            print(signature_url)

            # Separate the metadata from the image data
            head, data = signature_url.split(",", 1)

            # Get the file extension (gif, jpeg, png)
            file_ext = head.split(";")[0].split("/")[1]

            # Decode the image data
            plain_data = base64.b64decode(data)

            # # Write the image to a file
            with open("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + currently_loggedin_user.username + "." + file_ext, "wb") as f:
                f.write(plain_data)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "esignature_exist": esignature_exist,
    }

    return render(request, "dit-head-panel-invitation-bet-3.html", context)


# DIT Head - BET3 - Topic - Panel Invitation - Accept w/ Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3TopicPanelInvitationAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        get_panel_invitations = TitlePanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "pending"
        check_panel_invitation.save()

        get_panel_invitations = TitlePanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("DIT Head - Topic Panel Invitation doesn't exist.")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - BET3 - Topic - Panel Invitation - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelInvitationBet3Accept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date

        check_panel_invitation.panel_response = "pending"

        check_panel_invitation.save()

        get_panel_invitations = TitlePanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - BET3 - Topic - Panel Invitation - Decline w/ Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3TopicPanelInvitationDeclineSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        get_panel_invitations = TitlePanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    # BET-3 - Topic - Panel Invitation
    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = TitlePanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = TitlePanelInvitationLog(
            student_leader_username=check_updated_panel_invitation.student_leader_username,
            student_leader_full_name=check_updated_panel_invitation.student_leader_full_name,
            course_major_abbr=check_updated_panel_invitation.course_major_abbr,
            dit_head_username=check_updated_panel_invitation.dit_head_username,
            dit_head_full_name=check_updated_panel_invitation.dit_head_full_name,
            dit_head_response=check_updated_panel_invitation.dit_head_response,
            dit_head_response_date=check_updated_panel_invitation.dit_head_response_date,
            dit_head_signature=check_updated_panel_invitation.dit_head_signature,
            panel_username=check_updated_panel_invitation.panel_username,
            panel_full_name=check_updated_panel_invitation.panel_full_name,
            panel_response=check_updated_panel_invitation.panel_response,
            panel_response_date=check_updated_panel_invitation.panel_response_date,
            panel_signature=check_updated_panel_invitation.panel_signature,
            panel_attendance=check_updated_panel_invitation.panel_attendance,
            research_title_defense_date=check_updated_panel_invitation.research_title_defense_date,
            research_title_defense_start_time=check_updated_panel_invitation.research_title_defense_start_time,
            research_title_defense_end_time=check_updated_panel_invitation.research_title_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

        panel_invitation_bet3_check = TitlePanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "panel_invitations": panel_invitation_bet3_check, "declined_student_member_name": check_panel_invitation.student_leader_full_name, "declined_student_member_username": check_panel_invitation.student_leader_username, "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - Panel Invitation BET-3 Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelInvitationBet3Decline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = TitlePanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = TitlePanelInvitationLog(
            student_leader_username=check_updated_panel_invitation.student_leader_username,
            student_leader_full_name=check_updated_panel_invitation.student_leader_full_name,
            course_major_abbr=check_updated_panel_invitation.course_major_abbr,
            dit_head_username=check_updated_panel_invitation.dit_head_username,
            dit_head_full_name=check_updated_panel_invitation.dit_head_full_name,
            dit_head_response=check_updated_panel_invitation.dit_head_response,
            dit_head_response_date=check_updated_panel_invitation.dit_head_response_date,
            panel_username=check_updated_panel_invitation.panel_username,
            panel_full_name=check_updated_panel_invitation.panel_full_name,
            panel_response=check_updated_panel_invitation.panel_response,
            panel_response_date=check_updated_panel_invitation.panel_response_date,
            panel_attendance=check_updated_panel_invitation.panel_attendance,
            research_title_defense_date=check_updated_panel_invitation.research_title_defense_date,
            research_title_defense_start_time=check_updated_panel_invitation.research_title_defense_start_time,
            research_title_defense_end_time=check_updated_panel_invitation.research_title_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

        panel_invitation_bet3_check = TitlePanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "panel_invitations": panel_invitation_bet3_check, "declined_student_member_name": check_panel_invitation.student_leader_full_name, "declined_student_member_username": check_panel_invitation.student_leader_username, "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - BET3 - Proposal Defense - Panel Invitation - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3ProposalDefensePanelInvitationDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        esignature_exist = "True"
        print("E-sign exist")

    else:
        esignature_exist = "False"
        print("E-sign doesn't exist.")

    # PANEL INVITATION BET-3
    get_panel_invitation = ProposalPanelInvitation.objects.all().filter(dit_head_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "esignature_exist": esignature_exist,
    }

    return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)


# DIT Head - BET3 - Proposal - Panel Invitation - Accept w/ Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3ProposalPanelInvitationAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "pending"
        check_panel_invitation.save()

        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("DIT Head - Topic Panel Invitation doesn't exist.")
        return redirect("dit-head-bet3-proposal-defense-panel-invitation-dashboard")


# DIT Head - BET3 - Proposal - Panel Invitation - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3ProposalPanelInvitationAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date

        check_panel_invitation.panel_response = "pending"

        check_panel_invitation.save()

        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-proposal-defense-panel-invitation-dashboard")


# DIT Head - BET3 - Proposal - Panel Invitation - Decline w/ Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3ProposalPanelInvitationDeclineSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    # BET-3 - Topic - Panel Invitation
    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = ProposalPanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = ProposalPanelInvitationLog(
            student_leader_username=check_updated_panel_invitation.student_leader_username,
            student_leader_full_name=check_updated_panel_invitation.student_leader_full_name,
            course_major_abbr=check_updated_panel_invitation.course_major_abbr,
            dit_head_username=check_updated_panel_invitation.dit_head_username,
            dit_head_full_name=check_updated_panel_invitation.dit_head_full_name,
            dit_head_response=check_updated_panel_invitation.dit_head_response,
            dit_head_response_date=check_updated_panel_invitation.dit_head_response_date,
            dit_head_signature=check_updated_panel_invitation.dit_head_signature,
            panel_username=check_updated_panel_invitation.panel_username,
            panel_full_name=check_updated_panel_invitation.panel_full_name,
            panel_response=check_updated_panel_invitation.panel_response,
            panel_response_date=check_updated_panel_invitation.panel_response_date,
            panel_signature=check_updated_panel_invitation.panel_signature,
            panel_attendance=check_updated_panel_invitation.panel_attendance,
            research_proposal_defense_date=check_updated_panel_invitation.research_proposal_defense_date,
            research_proposal_defense_start_time=check_updated_panel_invitation.research_proposal_defense_start_time,
            research_proposal_defense_end_time=check_updated_panel_invitation.research_proposal_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

        panel_invitation_bet3_check = ProposalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "panel_invitations": panel_invitation_bet3_check, 
            "declined_student_member_name": check_panel_invitation.student_leader_full_name, 
            "declined_student_member_username": check_panel_invitation.student_leader_username, 
            "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-proposal-defense-panel-invitation-dashboard")


# DIT Head - Panel Invitation BET-3 Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3ProposalPanelInvitationDecline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = ProposalPanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = ProposalPanelInvitationLog(
            student_leader_username=check_updated_panel_invitation.student_leader_username,
            student_leader_full_name=check_updated_panel_invitation.student_leader_full_name,
            course_major_abbr=check_updated_panel_invitation.course_major_abbr,
            dit_head_username=check_updated_panel_invitation.dit_head_username,
            dit_head_full_name=check_updated_panel_invitation.dit_head_full_name,
            dit_head_response=check_updated_panel_invitation.dit_head_response,
            dit_head_response_date=check_updated_panel_invitation.dit_head_response_date,
            panel_username=check_updated_panel_invitation.panel_username,
            panel_full_name=check_updated_panel_invitation.panel_full_name,
            panel_response=check_updated_panel_invitation.panel_response,
            panel_response_date=check_updated_panel_invitation.panel_response_date,
            panel_attendance=check_updated_panel_invitation.panel_attendance,
            research_proposal_defense_date=check_updated_panel_invitation.research_proposal_defense_date,
            research_proposal_defense_start_time=check_updated_panel_invitation.research_proposal_defense_start_time,
            research_proposal_defense_end_time=check_updated_panel_invitation.research_proposal_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

        panel_invitation_bet3_check = ProposalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "panel_invitations": panel_invitation_bet3_check, 
            "declined_student_member_name": check_panel_invitation.student_leader_full_name, 
            "declined_student_member_username": check_panel_invitation.student_leader_username, 
            "response": "sweet panel invitation bet-3 declined"
            }

        return render(request, "dit-head-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - BET-3 Adviser Conforme Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3AdviserConforme(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 - Get Adviser Conforme
    get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "adviser_conformes": get_adviser_conforme,
    }

    return render(request, "dit-head-bet3-adviser-conforme.html", context)


# DIT Head - BET-3 Adviser Conforme - Accept with signature Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3AdviserConformeAcceptSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.dit_head_response = "Accepted"
        check_adviser_conforme.dit_head_response_date = date_today
        check_adviser_conforme.dit_head_signature = True

        check_adviser_conforme.adviser_response = "Pending"
        check_adviser_conforme.save()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "accepted_student_member_name": check_adviser_conforme.student_leader_full_name,
            "accepted_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme accepted",
        }

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT Head - BET-3 Adviser Conforme - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3AdviserConformeAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.dit_head_response = "Accepted"
        check_adviser_conforme.dit_head_response_date = date_today

        check_adviser_conforme.adviser_response = "Pending"
        check_adviser_conforme.save()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "accepted_student_member_name": check_adviser_conforme.student_leader_full_name,
            "accepted_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme accepted",
        }

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT Head - BET-3 Adviser Conforme - Decline with signature Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3AdviserConformeDeclineSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # Check if E-Sign Exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("DIT Head - E-sign exist")

    else:
        print("DIT Head - E-sign doesn't exist.")
        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=int(id))

        check_adviser_conforme.dit_head_response = "Declined"
        check_adviser_conforme.dit_head_response_date = dit_head_response_date
        check_adviser_conforme.dit_head_signature = True
        check_adviser_conforme.form_status = "Declined - DIT Head"

        check_adviser_conforme.adviser_response = "N/A"
        check_adviser_conforme.adviser_response_date = "N/A"

        check_adviser_conforme.save()

        check_updated_adviser_conforme = AdviserConforme.objects.get(id=int(id))

        log_adviser_conforme = AdviserConformeLog(
            student_leader_username=check_updated_adviser_conforme.student_leader_username,
            student_leader_full_name=check_updated_adviser_conforme.student_leader_full_name,
            course=check_updated_adviser_conforme.course,
            research_title=check_updated_adviser_conforme.research_title,
            form_date_submitted=check_updated_adviser_conforme.form_date_submitted,
            dit_head_username=check_updated_adviser_conforme.dit_head_username,
            dit_head_name=check_updated_adviser_conforme.dit_head_name,
            dit_head_response=check_updated_adviser_conforme.dit_head_response,
            dit_head_response_date=check_updated_adviser_conforme.dit_head_response_date,
            dit_head_signature=check_updated_adviser_conforme.dit_head_signature,
            adviser_username=check_updated_adviser_conforme.adviser_username,
            adviser_name=check_updated_adviser_conforme.adviser_name,
            adviser_response=check_updated_adviser_conforme.adviser_response,
            adviser_response_date=check_updated_adviser_conforme.adviser_response_date,
            form_status=check_updated_adviser_conforme.form_status,
        )
        log_adviser_conforme.save()

        check_updated_adviser_conforme.delete()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "adviser_conformes": get_adviser_conforme, "declined_student_member_name": check_adviser_conforme.student_leader_full_name, "declined_student_member_username": check_adviser_conforme.student_leader_username, "response": "sweet bet-3 adviser conforme declined"}

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT Head - BET-3 Adviser Conforme - Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3AdviserConformeDecline(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=int(id))

        check_adviser_conforme.dit_head_response = "Declined"
        check_adviser_conforme.dit_head_response_date = dit_head_response_date
        check_adviser_conforme.form_status = "Declined - DIT Head"

        check_adviser_conforme.adviser_response = "N/A"
        check_adviser_conforme.adviser_response_date = "N/A"

        check_adviser_conforme.save()

        check_updated_adviser_conforme = AdviserConforme.objects.get(id=int(id))

        log_adviser_conforme = AdviserConformeLog(
            student_leader_username=check_updated_adviser_conforme.student_leader_username,
            student_leader_full_name=check_updated_adviser_conforme.student_leader_full_name,
            course=check_updated_adviser_conforme.course,
            research_title=check_updated_adviser_conforme.research_title,
            form_date_submitted=check_updated_adviser_conforme.form_date_submitted,
            dit_head_username=check_updated_adviser_conforme.dit_head_username,
            dit_head_name=check_updated_adviser_conforme.dit_head_name,
            dit_head_response=check_updated_adviser_conforme.dit_head_response,
            dit_head_response_date=check_updated_adviser_conforme.dit_head_response_date,
            adviser_username=check_updated_adviser_conforme.adviser_username,
            adviser_name=check_updated_adviser_conforme.adviser_name,
            adviser_response=check_updated_adviser_conforme.adviser_response,
            adviser_response_date=check_updated_adviser_conforme.adviser_response_date,
            form_status=check_updated_adviser_conforme.form_status,
        )
        log_adviser_conforme.save()

        check_updated_adviser_conforme.delete()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "adviser_conformes": get_adviser_conforme, "declined_student_member_name": check_adviser_conforme.student_leader_full_name, "declined_student_member_username": check_adviser_conforme.student_leader_username, "response": "sweet bet-3 adviser conforme declined"}

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT Head - Panel Conforme BET-3 Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelConformeBet3(request):
    currently_loggedin_user = request.user

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
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_conforme_bet3_check": panel_conforme_bet3_check,
        }

        return render(request, "dit-head-panel-conforme-bet-3.html", context)

    except:
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        }

        return render(request, "dit-head-panel-conforme-bet-3.html", context)


# DIT Head - Panel Conforme BET-3 Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelConformeBet3Accept(request, id):
    currently_loggedin_user = request.user

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
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_conforme_bet3_check": panel_conforme_bet3_check,
            "accepted_research_title": panel_conforme_bet3_check_form.research_title,
            "response": "sweet panel conforme bet-3 accepted",
        }

        return render(request, "dit-head-panel-conforme-bet-3.html", context)

    except:
        return redirect("dit-head-panel-conforme-bet-3.html")


# DIT Head - Panel Conforme BET-3 Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadPanelConformeBet3Decline(request, id):
    pass


# DIT Head - BET-3 Panel Invitation Logs
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def ditHeadBET3PanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = TitlePanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    get_panel_invitation_2 = TitlePanelInvitationLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "dit-head-bet3-panel-invitation-logs.html", context)


##########################################################################################################################


# Panel - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,

        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,

        "today_proposal_defense": get_today_proposal_defense,
        "today_proposal_defense_present": get_today_proposal_defense_present,
        "completed_proposal_defense": get_completed_proposal_defense,
    }

    return render(request, "panel-dashboard.html", context)


# Panel - Research Title Defense Day Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelTitleDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if get_student_leader_data.research_title_defense_date != date_today:
        return redirect("panel-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username)

    get_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="")

    get_present_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="present")
    get_absent_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="absent")

    get_current_panel_title_defense = TitleDefenseForm.objects.get(student_leader_username=id, panel_attendance="present", panel_username=currently_loggedin_user.username)
    get_present_panel_members_title_defense = TitleDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")
    get_panel_chairman = TitleDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present", is_panel_chairman=1)

    check_panel_complete_response = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username, panel_response="")

    get_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)

    try:
        check_start_voting = TitleDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1)
    except:
       check_start_voting = 0

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Revise Title")
    except:
        get_research_title_revise = None

    try:
        check_panel_mark_done = TitleDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, form_status="")
    except:
        check_panel_mark_done = None


    try:
        get_no_response_signature = TitleDefenseForm.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)
        get_no_response_signature = 1
    except:
        get_no_response_signature = 0

    print(check_panel_complete_response)
    print(check_start_voting)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "research_titles": get_research_titles,
        "panel_members": get_panel_members,
        "present_panel_members": get_present_panel_members,
        "absent_panel_members": get_absent_panel_members,
        "current_panel_title_defense": get_current_panel_title_defense,
        "present_panel_members_title_defense": get_present_panel_members_title_defense,
        "panel_chairman": get_panel_chairman,
        "check_panel_complete_response": check_panel_complete_response,
        "check_panel_mark_done": check_panel_mark_done,
        "research_title_data": get_research_title_data,
        "research_title_accepted": get_research_title_accepted,
        "research_title_revise": get_research_title_revise,
        "start_voting": check_start_voting,
        "response_signature": get_no_response_signature
    }

    return render(request, "panel-title-defense-day.html", context)


# Panel - Live Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelTitleDefenseDayLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet no esign"
        }

        return render(request, "panel-dashboard.html", context)
    
    try:
        get_no_response_signature = TitleDefenseForm.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)
        
        get_no_response_signature.panel_signature_response = True
        get_no_response_signature.save()


        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet live signature respond"
        }

        return render(request, "panel-dashboard.html", context)

    except:

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet signature already respond"
        }

        return render(request, "panel-dashboard.html", context)


# Panel - Attach Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelTitleDefenseDayAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet no esign"
        }

        return render(request, "panel-dashboard.html", context)
    
    try:
        get_no_response_signature = TitleDefenseForm.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)
        
        get_no_response_signature.panel_signature_response = True
        get_no_response_signature.panel_signature_attach = True
        get_no_response_signature.save()


        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet attach signature respond"
        }

        return render(request, "panel-dashboard.html", context)

    except:

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet signature already respond"
        }

        return render(request, "panel-dashboard.html", context)


# Panel - Accept Title Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelAcceptTitle(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    update_title = TitleVote.objects.get(id=id)
    update_title.panel_response = "accepted"
    update_title.panel_response_date = date_today
    update_title.save()

    update_accepted_count = ResearchTitle.objects.get(research_title=update_title.research_title)
    update_accepted_count.accepted = update_accepted_count.accepted + 1
    update_accepted_count.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "accepted_research_title": update_title.research_title, 
        "student_username": update_title.student_leader_username, 
        "response": "sweet title accepted"
        }

    return render(request, "panel-dashboard.html", context)


# Panel - Defer Title Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelDeferTitle(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    update_title = TitleVote.objects.get(id=id)
    update_title.panel_response = "deferred"
    update_title.panel_response_date = date_today
    update_title.save()

    update_deferred_count = ResearchTitle.objects.get(research_title=update_title.research_title)
    update_deferred_count.deferred = update_deferred_count.deferred + 1
    update_deferred_count.save()

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "deferred_research_title": update_title.research_title, "student_username": update_title.student_leader_username, "response": "sweet title deferred"}

    return render(request, "panel-dashboard.html", context)


# Panel - Revise Title Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelReviseTitle(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    update_title = TitleVote.objects.get(id=id)
    update_title.panel_response = "revise title"
    update_title.panel_response_date = date_today
    update_title.save()

    update_revise_title_count = ResearchTitle.objects.get(research_title=update_title.research_title)
    update_revise_title_count.revise_title = update_revise_title_count.revise_title + 1
    update_revise_title_count.save()

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "revise_research_title": update_title.research_title, "student_username": update_title.student_leader_username, "response": "sweet revise title"}

    return render(request, "panel-dashboard.html", context)


# Panel - Title Defense Mark as Done Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelTitleDefenseMarkDone(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        update_panel_title_defense = TitleDefenseForm.objects.get(id=id)
    except:
        return redirect("panel-dashboard")

    update_panel_title_defense.form_status = "completed"
    update_panel_title_defense.save()

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "student_username": update_panel_title_defense.student_leader_username, "response": "sweet mark as done"}

    return render(request, "panel-dashboard.html", context)

##### PROPOSAL DEFENSE #####

# Panel - Research Proposal Defense Day Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if get_student_leader_data.research_proposal_defense_date != date_today:
        return redirect("panel-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    # get_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="")

    # get_present_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="present")
    # get_absent_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="absent")

    # get_current_panel_title_defense = TitleDefenseForm.objects.get(student_leader_username=id, panel_attendance="present", panel_username=currently_loggedin_user.username)
    get_present_panel_members_proposal_defense = ProposalDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")
    # get_panel_chairman = TitleDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present", is_panel_chairman=1)

    # check_panel_complete_response = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username, panel_response="")

    # get_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)


    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        return redirect("subject-teacher-dashboard")

    get_critique_panel_chairman_signature_all = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman = True, panel_chairman_signature_response = False)
    
    if not get_critique_panel_chairman_signature_all:
        get_critique_panel_chairman_signature_all = 0
    else:
        get_critique_panel_chairman_signature_all = 1

    get_critique_panel_signature_all = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)
    
    if not get_critique_panel_signature_all:
        get_critique_panel_signature_all = 0
    else:
        get_critique_panel_signature_all = 1


    try:
        check_panel_critique = ProposalDefenseCritique.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username)
    except:
        check_panel_critique = None

    try:
        check_start_critique = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_critique=1)
    except:
        check_start_critique = 0

    try:
        check_end_critique = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, end_critique=1)
    except:
        check_end_critique = 0

    try:
        get_panel_critique = ProposalDefenseCritique.objects.all().filter(student_leader_username=id, panel_username = request.user, panel_attendance="present")
    except:
        get_panel_critique = None

    try:
        check_start_voting = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1)
    except:
        check_start_voting = 0
    
    try:
        check_pending_pc_panel_defense_signature = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1, panel_chairman_signature_response = False)
    except:
        check_pending_pc_panel_defense_signature = 0
    
    
    # try:
    #     check_panel_mark_done = TitleDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, form_status="")
    # except:
    #     check_panel_mark_done = None


    # try:
    #     get_no_response_signature = TitleDefenseForm.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)
    #     get_no_response_signature = 1
    # except:
    #     get_no_response_signature = 0

    # print(check_panel_complete_response)
    # print(check_start_voting)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,

        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "accepted_research_title": get_accepted_research_title,
        # "research_titles": get_research_titles,
        # "panel_members": get_panel_members,
        # "present_panel_members": get_present_panel_members,
        # "absent_panel_members": get_absent_panel_members,
        # "current_panel_title_defense": get_current_panel_title_defense,
        "present_panel_members_proposal_defense": get_present_panel_members_proposal_defense,

        "critique_panel_chairman_signature_response_all": get_critique_panel_chairman_signature_all,
        "critique_panel_signature_response_all": get_critique_panel_signature_all,
        # "panel_chairman": get_panel_chairman,
        # "check_panel_complete_response": check_panel_complete_response,
        # "check_panel_mark_done": check_panel_mark_done,
        # "research_title_data": get_research_title_data,
        # "research_title_accepted": get_research_title_accepted,
        # "research_title_revise": get_research_title_revise,
        "start_critique": check_start_critique,
        "end_critique": check_end_critique,
        "panel_critique": get_panel_critique,
        "check_panel_critique": check_panel_critique,
        "start_voting": check_start_voting,
        "student_username": id,
        # "response_signature": get_no_response_signature
    }

    return render(request, "panel-bet3-proposal-defense-day.html", context)


# Panel - BET-3 - Proposal Defense - Panel Chairman attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayPanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    
    try:
        get_no_response_signature = ProposalDefenseForm.objects.get(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_chairman_signature_response = False)
        
        get_no_response_signature.panel_chairman_signature_response = True
        get_no_response_signature.panel_chairman_signature_attach = True
        get_no_response_signature.save()


        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense attach signature respond"
        }

        return render(request, "panel-dashboard.html", context)

    except:

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense signature already respond"
        }

        return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Save Critique
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDaySaveCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None
    
    if request.method == "POST":
        critique = request.POST.get("critique_input")
        print("Critique: ", critique)

        check_end_voting = ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username=currently_loggedin_user.username, end_critique=1)

        if check_end_voting:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "panel_data": get_panel_data,

                "today_title_defense": get_today_title_defense,
                "today_title_defense_present": get_today_title_defense_present,
                "completed_title_defense": get_completed_title_defense,

                "today_proposal_defense": get_today_proposal_defense,
                "today_proposal_defense_present": get_today_proposal_defense_present,
                "completed_proposal_defense": get_completed_proposal_defense,

                "student_username": id,

                "response": "sweet critique form has ended",
                }

            return render(request, "panel-dashboard.html", context)
        else:
            save_critique = ProposalDefenseCritique(
                student_leader_username = get_student_proposal_defense_form.student_leader_username,
                student_leader_full_name = get_student_proposal_defense_form.student_leader_full_name,
                course_major_abbr = get_student_proposal_defense_form.course_major_abbr,

                panel_username = get_student_proposal_defense_form.panel_username,
                panel_full_name = get_student_proposal_defense_form.panel_full_name,
                panel_attendance = get_student_proposal_defense_form.panel_attendance,
                panel_signature_response = get_student_proposal_defense_form.panel_signature_response,
                panel_signature_attach = get_student_proposal_defense_form.panel_signature_attach,
                is_panel_chairman = get_student_proposal_defense_form.is_panel_chairman,
                panel_chairman_signature_response = get_student_proposal_defense_form.panel_chairman_signature_response,
                panel_chairman_signature_attach = get_student_proposal_defense_form.panel_chairman_signature_attach,

                form_date = date_today,

                critique = critique,

                form_status = get_student_proposal_defense_form.form_status,
                form = "Critique Form",

                subject_teacher_username = get_student_proposal_defense_form.subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_defense_form.subject_teacher_full_name,

                defense_date = get_student_proposal_defense_form.defense_date,
                defense_start_time = get_student_proposal_defense_form.defense_start_time,
                defense_end_time = get_student_proposal_defense_form.defense_end_time,
                )
            save_critique.save()

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "panel_data": get_panel_data,

                "today_title_defense": get_today_title_defense,
                "today_title_defense_present": get_today_title_defense_present,
                "completed_title_defense": get_completed_title_defense,

                "today_proposal_defense": get_today_proposal_defense,
                "today_proposal_defense_present": get_today_proposal_defense_present,
                "completed_proposal_defense": get_completed_proposal_defense,

                "student_username": id,

                "response": "sweet proposal defense critique saved",
            }

            return render(request, "panel-dashboard.html", context)

            

# Panel - BET-3 - Proposal Defense - Delete Critique
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayDeleteCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None

    
    try:
        delete_critique = ProposalDefenseCritique.objects.get(panel_username=request.user, id=id)
        student_username = delete_critique.student_leader_username
        print(delete_critique.critique)
        delete_critique.delete()
        
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,

            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,

            "today_proposal_defense": get_today_proposal_defense,
            "today_proposal_defense_present": get_today_proposal_defense_present,
            "completed_proposal_defense": get_completed_proposal_defense,

            "student_username": student_username,

            "response": "sweet proposal defense critique deleted",
        }

        return render(request, "panel-dashboard.html", context)

    except:
        
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,

            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,

            "today_proposal_defense": get_today_proposal_defense,
            "today_proposal_defense_present": get_today_proposal_defense_present,
            "completed_proposal_defense": get_completed_proposal_defense,

            "student_username": id,

            "response": "sweet proposal defense critique not found",
        }

        return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Critique Form -  Panel Chairman attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayCritiquePanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel Chairman - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    

    get_all_panel_chairman_no_esign_response = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)
    
    if get_all_panel_chairman_no_esign_response:
        for i in range(len(get_all_panel_chairman_no_esign_response)):
            get_all_panel_chairman_no_esign_response[i].panel_chairman_signature_response = True
            get_all_panel_chairman_no_esign_response[i].panel_chairman_signature_attach = True
            get_all_panel_chairman_no_esign_response[i].save()
            i + 1
    
    if get_student_proposal_defense_form.is_panel_chairman == True and get_all_panel_chairman_no_esign_response[0].is_panel_chairman == True and get_all_panel_chairman_no_esign_response[0].panel_signature_response == True:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
    


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet critique panel chairman esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Critique Form -  Panel attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayCritiquePanelAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None

    

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel Chairman - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense no esign"
        }

        return render(request, "panel-dashboard.html", context)


    get_all_panel_no_esign_response = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)

    if get_all_panel_no_esign_response:
        for i in range (len(get_all_panel_no_esign_response)):
            get_all_panel_no_esign_response[i].panel_signature_response = True
            get_all_panel_no_esign_response[i].panel_signature_attach = True
            get_all_panel_no_esign_response[i].save()
            i + 1
        print("Panel Critique Signature Response Updated")
    
        # Student Leader - Get Student Proposal Defense Form Data

    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        pass

    
    if get_student_proposal_defense_form.is_panel_chairman == True and get_all_panel_no_esign_response[0].is_panel_chairman == True and get_all_panel_no_esign_response[0].panel_chairman_signature_response == True:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
        print("Panel Chairman Proposal Defense Updated")
    
    if get_student_proposal_defense_form.is_panel_chairman == False and get_all_panel_no_esign_response[0].is_panel_chairman == False:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
        print("Panel Proposal Defense Updated")
    

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet critique panel esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Critique Form -  Panel Chairman attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayCritiquePanelChairmanLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None
  

    get_all_panel_chairman_no_esign_response = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)
    
    if get_all_panel_chairman_no_esign_response:
        for i in range(len(get_all_panel_chairman_no_esign_response)):
            get_all_panel_chairman_no_esign_response[i].panel_chairman_signature_response = True
            get_all_panel_chairman_no_esign_response[i].save()
            i + 1
    
    if get_student_proposal_defense_form.is_panel_chairman == True and get_all_panel_chairman_no_esign_response[0].is_panel_chairman == True and get_all_panel_chairman_no_esign_response[0].panel_signature_response == True:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
    

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet critique panel chairman esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Critique Form -  Panel attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayCritiquePanelLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None


    get_all_panel_no_esign_response = ProposalDefenseCritique.objects.all().filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)

    if get_all_panel_no_esign_response:
        for i in range (len(get_all_panel_no_esign_response)):
            get_all_panel_no_esign_response[i].panel_signature_response = True
            get_all_panel_no_esign_response[i].save()
            i + 1
        print("Panel Critique Signature Response Updated")
    
        # Student Leader - Get Student Proposal Defense Form Data

    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        pass

    
    if get_student_proposal_defense_form.is_panel_chairman == True and get_all_panel_no_esign_response[0].is_panel_chairman == True and get_all_panel_no_esign_response[0].panel_chairman_signature_response == True:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
        print("Panel Chairman Proposal Defense Updated")
    
    if get_student_proposal_defense_form.is_panel_chairman == False and get_all_panel_no_esign_response[0].is_panel_chairman == False:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user).update(critique_sign_response = True)
        print("Panel Proposal Defense Updated")
    

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet critique panel live sign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense - Accepted with Revision
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None

    
    try:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, proposal_defense_response="").update(proposal_defense_response = "Accepted with Revision")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,

            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,

            "today_proposal_defense": get_today_proposal_defense,
            "today_proposal_defense_present": get_today_proposal_defense_present,
            "completed_proposal_defense": get_completed_proposal_defense,

            "student_username": id,
            "response": "sweet proposal defense accepted with revision"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")
    

# Panel - BET-3 - Proposal Defense - Deferred with Revision
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayDeferred(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None

    
    try:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, proposal_defense_response="").update(proposal_defense_response = "Deferred with Revision")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,

            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,

            "today_proposal_defense": get_today_proposal_defense,
            "today_proposal_defense_present": get_today_proposal_defense_present,
            "completed_proposal_defense": get_completed_proposal_defense,

            "student_username": id,
            "response": "sweet proposal defense deferred with revision"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")


# Panel - BET-3 - Proposal Defense - Not Accepted
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayNotAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="")
    get_today_title_defense_present = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_title_defense_date=today.strftime("%B %d, %Y"), form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_title_defense_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_title_defense_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_title_defense_data.username, name=get_student_title_defense_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    get_today_proposal_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_proposal_defense_present = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_proposal_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_proposal_defense_data = StudentLeader.objects.get(username=get_today_proposal_defense.student_leader_username)
    except:
        get_student_proposal_defense_data = None

    try:
        get_completed_proposal_defense = DefenseSchedule.objects.get(student_leader_username=get_student_proposal_defense_data.username, name=get_student_proposal_defense_data.bet3_subject_teacher_name, form="Research Proposal Defense", date=date_today, status="Completed")
    except:
        get_completed_proposal_defense = None

    
    try:
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, proposal_defense_response="").update(proposal_defense_response = "Not Accpeted")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,

            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,

            "today_proposal_defense": get_today_proposal_defense,
            "today_proposal_defense_present": get_today_proposal_defense_present,
            "completed_proposal_defense": get_completed_proposal_defense,

            "student_username": id,
            "response": "sweet proposal defense not accepted"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")


# Panel - BET-3 - Proposal Defense Form - Panel Chairman attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayPanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel Chairman - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    

    try:
        ProposalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)\
        .update(panel_chairman_signature_response = True, panel_chairman_signature_attach = True)
    except:
        pass
    
    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet proposal panel chairman esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense Form - Panel attach signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayPanelAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel Chairman - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "panel_data": get_panel_data,
            "today_title_defense": get_today_title_defense,
            "today_title_defense_present": get_today_title_defense_present,
            "completed_title_defense": get_completed_title_defense,
            "student_username" : id,
            "response": "sweet proposal defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    

    try:
        ProposalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)\
        .update(panel_signature_response = True, panel_signature_attach = True)
    except:
        pass
    
    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet proposal panel esign"
    }

    return render(request, "panel-dashboard.html", context)

# Panel - BET-3 - Proposal Defense Form -  Panel Chairman live signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayPanelChairmanLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None

    try:
        ProposalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)\
        .update(panel_chairman_signature_response = True)
    except:
        pass
    
    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet proposal panel chairman live sign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-3 - Proposal Defense Form -  Panel Chairman live signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefenseDayPanelLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_title_defense = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_title_defense_present = ProposalDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username, defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_today_title_defense.student_leader_username)
    except:
        get_student_leader_data = None

    try:
        get_completed_title_defense = DefenseSchedule.objects.get(student_leader_username=get_student_leader_data.username, name=get_student_leader_data.bet3_subject_teacher_name, form="Research Title Defense", date=date_today, status="Completed")
    except:
        get_completed_title_defense = None
    
    # Student Leader - Get Student Proposal Defense Form Data
    try:
        get_student_proposal_defense_form = ProposalDefenseForm.objects.get(student_leader_username=id, panel_username = request.user)
    except:
        get_student_proposal_defense_form = None

    try:
        ProposalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)\
        .update(panel_signature_response = True)
    except:
        pass
    
    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "today_title_defense": get_today_title_defense,
        "today_title_defense_present": get_today_title_defense_present,
        "completed_title_defense": get_completed_title_defense,
        "student_username" : id,
        "response": "sweet proposal panel live sign"
    }

    return render(request, "panel-dashboard.html", context)


##### PROPOSAL DEFENSE END #####

# Panel - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelProfile(request):
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

    return render(request, "panel-profile.html", context)


# Panel - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelUploadESignature(request):
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

                    return render(request, "panel-profile.html", context)
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

                    return render(request, "panel-profile.html", context)

                return redirect("panel-profile")

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

            return render(request, "panel-profile.html", context)


# Panel - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("panel-profile")


# Panel - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelCreateESignature(request):
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

        return redirect("panel-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "panel-signature-pad.html", context)


# Panel - Acount Settings Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelAccountSettings(request):
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

                    return render(request, "panel-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "panel-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "panel-account-settings.html", context)

    return render(request, "panel-account-settings.html", context)


# Panel - BET3 - Topic Defense - Panel Invitation - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelPanelInvitationBet3(request):
    currently_loggedin_user = request.user
    print("Current User:", currently_loggedin_user.username)

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # PANEL INVITATION BET-3
    get_panel_invitation = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "panel_invitations": get_panel_invitation}

    return render(request, "panel-panel-invitation-bet-3.html", context)


# Panel - BET3 - Topic Defense - Panel Invitation - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3TopicPanelInvitationAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_panel_invitations = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-invitation-bet-3")


# Panel - BET3 - Topic Defense - Panel Invitation - Decline with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3TopicPanelInvitationDeclineSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_panel_invitations = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True
        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-invitation-bet-3")


# Panel - BET3 - Topic Defense - Panel Invitation - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelPanelInvitationBet3Accept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-invitation-bet-3")


# Panel - Panel Invitation BET-3 Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelPanelInvitationBet3Decline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = TitlePanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-invitation-bet-3")


# Panel - Research Title Defense Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def panelResearchTitleDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_panel_research_title_defense_form = TitleDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username)

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account}

    return render(request, "panel-research-title-defense-dashboard.html", context)


# Panel - Panel Conforme BET-3 Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelPanelConformeBet3(request):
    currently_loggedin_user = request.user

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
        panel_conforme_bet3_check_1 = PanelConformeBET3.objects.all().filter(panel_member_1=currently_loggedin_user.username, panel_member_status_1="pending")
    except:
        print("Not Panel 1")
        pass

    try:
        panel_conforme_bet3_check_2 = PanelConformeBET3.objects.all().filter(panel_member_2=currently_loggedin_user.username, panel_member_status_2="pending")
    except:
        print("Not Panel 2")
        pass

    try:
        panel_conforme_bet3_check_3 = PanelConformeBET3.objects.all().filter(panel_member_3=currently_loggedin_user.username, panel_member_status_3="pending")
    except:
        print("Not Panel 3")
        pass

    try:
        panel_conforme_bet3_check_4 = PanelConformeBET3.objects.all().filter(panel_member_4=currently_loggedin_user.username, panel_member_status_4="pending")
    except:
        print("Not Panel 4")
        pass

    try:
        panel_conforme_bet3_check_5 = PanelConformeBET3.objects.all().filter(panel_member_5=currently_loggedin_user.username, panel_member_status_5="pending")
    except:
        print("Not Panel 5")
        pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_conforme_bet3_check_1": panel_conforme_bet3_check_1,
        "panel_conforme_bet3_check_2": panel_conforme_bet3_check_2,
        "panel_conforme_bet3_check_3": panel_conforme_bet3_check_3,
        "panel_conforme_bet3_check_4": panel_conforme_bet3_check_4,
        "panel_conforme_bet3_check_5": panel_conforme_bet3_check_5,
    }

    return render(request, "panel-panel-conforme-bet-3.html", context)


# Panel - Panel Conforme BET-3 Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelPanelConformeBet3Accept(request, id):
    currently_loggedin_user = request.user

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
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_conforme_bet3_check": panel_conforme_bet3_check,
            "accepted_research_title": panel_conforme_bet3_check_form.research_title,
            "response": "sweet panel conforme bet-3 accepted",
        }

        return render(request, "panel-panel-conforme-bet-3.html", context)

    except:
        return redirect("panel-panel-conforme-bet-3.html")


# Panel - BET-3 Panel Invitation Logs
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3PanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username)
    get_panel_invitation_2 = TitlePanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "panel-bet3-panel-invitation-logs.html", context)


# Panel - BET-3 Title Defense Logs
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3TitleDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    completed_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)
    deferred_title_defense = TitlePanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)

    absent_title_defense = TitlePanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)
    absent_title_defense_log = TitlePanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)

    present_reschedule_title_defense = TitlePanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="present-reschedule")
    absent_reschedule_title_defense = TitlePanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="absent-reschedule")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
        "completed_title_defense": completed_title_defense,
        "deferred_title_defense": deferred_title_defense,
        "absent_title_defense": absent_title_defense,
        "absent_title_defense_log": absent_title_defense_log,
        "present_reschedule_title_defense": present_reschedule_title_defense,
        "absent_reschedule_title_defense": absent_reschedule_title_defense,
    }

    return render(request, "panel-bet3-research-title-defense-logs.html", context)


# Panel - BET-3 Title Defense Log Completed
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3TitleDefenseLogCompleted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-bet3-title-defense-logs")

    get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=id)
    get_present_panel_members = TitleDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")
    get_panel_title_votes = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username, panel_response_date=get_student_leader_data.research_title_defense_date)

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Revise Title")
    except:
        get_research_title_revise = None

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_student_group_members,
        "research_titles": get_research_titles,
        "research_title_accepted": get_research_title_accepted,
        "research_title_revise": get_research_title_revise,
        "present_panel_members": get_present_panel_members,
        "panel_title_votes": get_panel_title_votes,
    }

    return render(request, "panel-bet3-research-title-defense-data.html", context)


# Panel - BET-3 Title Defense Log Redefense
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3TitleDefenseLogRedefense(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-bet3-title-defense-logs")

    get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = ResearchTitleLog.objects.all().filter(student_leader_username=id)
    get_present_panel_members = TitleDefenseFormLog.objects.all().filter(student_leader_username=id, panel_attendance="present")
    get_panel_title_votes = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username, panel_response_date=get_present_panel_members[0].defense_date)

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_student_group_members,
        "research_titles": get_research_titles,
        "present_panel_members": get_present_panel_members,
        "panel_title_votes": get_panel_title_votes,
    }

    return render(request, "panel-bet3-research-title-defense-data.html", context)

##### PANEL - PROPOSAL DEFENSE #####

# Panel - BET3 - Proposal Defense - Panel Invitation - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalDefensePanelInvitationDashboard(request):
    currently_loggedin_user = request.user
    print("Current User:", currently_loggedin_user.username)

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # PANEL INVITATION BET-3
    get_panel_invitation = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "panel_invitations": get_panel_invitation}

    return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)


# Panel - BET3 - Proposal Defense - Panel Invitation - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalPanelInvitationAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet3-proposal-defense-panel-invitation-dashboard")


# Panel - BET3 - Proposal Defense - Panel Invitation - Decline with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalPanelInvitationDeclineSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_panel_invitations = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True
        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet3-proposal-defense-panel-invitation-dashboard")


# Panel - BET3 - Proposal Defense - Panel Invitation - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalPanelInvitationAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet3-proposal-defense-panel-invitation-dashboard")


# Panel - BET3 - Proposal Defense - Panel Invitation - Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_panel, login_url="index")
def panelBET3ProposalPanelInvitationDecline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = ProposalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-bet3-proposal-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet3-proposal-defense-panel-invitation-dashboard")


##########################################################################################################################

# Subject Teacher - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Student Leader - get data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("subject-teacher-dashboard")

    # If Student Defense Schedule and Date Today is not the same
    if get_student_leader_data.research_title_defense_date != today.strftime("%B %d, %Y"):
        return redirect("subject-teacher-dashboard")

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=id)

    get_bet3_panel_invitations = TitlePanelInvitation.objects.all().filter(student_leader_username=id)

    get_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", research_title_defense_date=date_today, panel_attendance="")

    get_present_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", research_title_defense_date=date_today, panel_attendance="present")
    get_absent_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", research_title_defense_date=date_today, panel_attendance="absent")

    get_present_panel_members_title_defense = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")
    get_panel_chairman = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present", is_panel_chairman=1)

    get_pending_title_defense_vote = TitleDefenseForm.objects.all().filter(student_leader_username=id, form_status="", defense_date=date_today)

    get_pending_signature_response = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_signature_response = 0)

    get_start_voting = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_signature_response = 1, start_voting = 1)

    try:
        check_accepted_title = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        check_accepted_title = None

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Revise Title")
    except:
        get_research_title_revise = None

    try:
        get_research_title_deferred = ResearchTitle.objects.all().filter(student_leader_username=id, status="Title Defense - Deferred")

        if get_research_title_deferred.count() == get_research_titles.count():
            all_deferred = 1
        else:
            all_deferred = 0

    except:
        all_deferred = 0

    try:
        get_student_title_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, date=date_today, status="Reserved")
    except:
        pass

    # Check if the Title Defense is Completed
    try:
        check_title_defense_completed = DefenseSchedule.objects.get(student_leader_username=id, date=date_today, status="Completed")
    except:
        check_title_defense_completed = None

    if not get_panel_members:
        if get_present_panel_members.count() < 3:
            print("Re Schedule")

            get_student_title_defense_schedule.status = "Reschedule"
            get_student_title_defense_schedule.save()

            # Get Updated Defense Schedule
            try:
                updated_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, date=date_today, status="Reschedule")

                log_defense_schedule = DefenseScheduleLog(
                    username=updated_defense_schedule.username, name=updated_defense_schedule.name, student_leader_username=updated_defense_schedule.student_leader_username, student_leader_name=updated_defense_schedule.student_leader_name, course=updated_defense_schedule.course, form=updated_defense_schedule.form, date=updated_defense_schedule.date, start_time=updated_defense_schedule.start_time, end_time=updated_defense_schedule.end_time, status=updated_defense_schedule.status
                )

                log_defense_schedule.save()

            except:
                updated_defense_schedule = None

            for i in range(len(get_bet3_panel_invitations)):
                log_panel_invitation = TitlePanelInvitationLog(
                    student_leader_username=get_bet3_panel_invitations[i].student_leader_username,
                    student_leader_full_name=get_bet3_panel_invitations[i].student_leader_full_name,
                    course_major_abbr=get_bet3_panel_invitations[i].course_major_abbr,
                    dit_head_username=get_bet3_panel_invitations[i].dit_head_username,
                    dit_head_full_name=get_bet3_panel_invitations[i].dit_head_full_name,
                    dit_head_response=get_bet3_panel_invitations[i].dit_head_response,
                    dit_head_response_date=get_bet3_panel_invitations[i].dit_head_response_date,
                    panel_username=get_bet3_panel_invitations[i].panel_username,
                    panel_full_name=get_bet3_panel_invitations[i].panel_full_name,
                    panel_response=get_bet3_panel_invitations[i].panel_response,
                    panel_response_date=get_bet3_panel_invitations[i].panel_response_date,
                    panel_attendance=get_bet3_panel_invitations[i].panel_attendance+"-reschedule",
                    research_title_defense_date=get_bet3_panel_invitations[i].research_title_defense_date,
                    research_title_defense_start_time=get_bet3_panel_invitations[i].research_title_defense_start_time,
                    research_title_defense_end_time=get_bet3_panel_invitations[i].research_title_defense_end_time,
                    form_date_sent=get_bet3_panel_invitations[i].form_date_sent,
                    form_status=get_bet3_panel_invitations[i].form_status,
                    form=get_bet3_panel_invitations[i].form,
                    subject_teacher_username=get_bet3_panel_invitations[i].subject_teacher_username,
                    subject_teacher_full_name=get_bet3_panel_invitations[i].subject_teacher_full_name,
                    is_completed=get_bet3_panel_invitations[i].is_completed,
                )
                log_panel_invitation.save()
                i + 1

            for i in range(len(get_present_panel_members_title_defense)):
                log_research_title_defense_form = TitleDefenseFormLog(
                    student_leader_username=get_present_panel_members_title_defense[i].student_leader_username,
                    student_leader_full_name=get_present_panel_members_title_defense[i].student_leader_full_name,
                    course_major_abbr=get_present_panel_members_title_defense[i].course_major_abbr,
                    panel_username=get_present_panel_members_title_defense[i].panel_username,
                    panel_full_name=get_present_panel_members_title_defense[i].panel_full_name,
                    panel_attendance=get_present_panel_members_title_defense[i].panel_attendance,
                    is_panel_chairman=get_present_panel_members_title_defense[i].is_panel_chairman,
                    form_date=get_present_panel_members_title_defense[i].form_date,
                    form_status=get_present_panel_members_title_defense[i].form_status,
                    form=get_present_panel_members_title_defense[i].form,
                    subject_teacher_username=get_present_panel_members_title_defense[i].subject_teacher_username,
                    subject_teacher_full_name=get_present_panel_members_title_defense[i].subject_teacher_full_name,
                    defense_date=get_present_panel_members_title_defense[i].defense_date,
                    defense_start_time=get_present_panel_members_title_defense[i].defense_start_time,
                    defense_end_time=get_present_panel_members_title_defense[i].defense_end_time,
                )
                log_research_title_defense_form.save()
                i + 1

            get_student_leader_data.research_title_defense_date = ""
            get_student_leader_data.research_title_defense_start_time = ""
            get_student_leader_data.research_title_defense_end_time = ""
            get_student_leader_data.request_limit = 5
            get_student_leader_data.bet3_panel_invitation_status = ""
            get_student_leader_data.save()

            get_bet3_panel_invitations.delete()
            get_present_panel_members_title_defense.delete()
            updated_defense_schedule.delete()

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "date_today": today.strftime("%B %d, %Y"), 
                "student_leader_full_name": student_leader_full_name, 

                "response": "sweet re-defense incomplete panel"}

            return render(request, "subject-teacher-dashboard.html", context)

    if request.method == "POST":
        suggest_title_input = request.POST.get("suggest_title_input")

        if suggest_title_input != None:
            get_research_title_revise.suggested_title = suggest_title_input.title()
            get_research_title_revise.save()

        for i in range(len(get_present_panel_members)):
            get_present_panel_members[i].is_completed = True
            get_present_panel_members[i].save()
            i + 1

        if get_research_title_deferred.count() == get_research_titles.count():
            print("all deferred")

            get_student_title_defense_schedule.status = "Re-Defense"
            get_student_title_defense_schedule.save()

            # Get Updated Defense Schedule
            try:
                updated_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, date=date_today, status="Re-Defense")

                log_defense_schedule = DefenseScheduleLog(
                    username=updated_defense_schedule.username, name=updated_defense_schedule.name, student_leader_username=updated_defense_schedule.student_leader_username, student_leader_name=updated_defense_schedule.student_leader_name, course=updated_defense_schedule.course, form=updated_defense_schedule.form, date=updated_defense_schedule.date, start_time=updated_defense_schedule.start_time, end_time=updated_defense_schedule.end_time, status=updated_defense_schedule.status
                )

                log_defense_schedule.save()

            except:
                updated_defense_schedule = None

            for i in range(len(get_research_titles)):
                log_research_titles = ResearchTitleLog(
                    research_title=get_research_titles[i].research_title,
                    course=get_research_titles[i].course,
                    major=get_research_titles[i].major,
                    course_major_abbr=get_research_titles[i].course_major_abbr,
                    student_leader_username=get_research_titles[i].student_leader_username,
                    student_leader_name=get_research_titles[i].student_leader_name,
                    status=get_research_titles[i].status,
                    date_submitted=get_research_titles[i].date_submitted,
                    accepted=get_research_titles[i].accepted,
                    deferred=get_research_titles[i].deferred,
                    revise_title=get_research_titles[i].revise_title,
                    suggested_title=get_research_titles[i].suggested_title,
                    old_research_title=get_research_titles[i].old_research_title,
                    defense_date=get_student_leader_data.research_title_defense_date,
                    title_defense_status=get_research_titles[i].title_defense_status,
                )
                log_research_titles.save()
                i + 1

            for i in range(len(get_bet3_panel_invitations)):
                log_panel_invitation = TitlePanelInvitationLog(
                    student_leader_username=get_bet3_panel_invitations[i].student_leader_username,
                    student_leader_full_name=get_bet3_panel_invitations[i].student_leader_full_name,
                    course_major_abbr=get_bet3_panel_invitations[i].course_major_abbr,
                    dit_head_username=get_bet3_panel_invitations[i].dit_head_username,
                    dit_head_full_name=get_bet3_panel_invitations[i].dit_head_full_name,
                    dit_head_response=get_bet3_panel_invitations[i].dit_head_response,
                    dit_head_response_date=get_bet3_panel_invitations[i].dit_head_response_date,
                    panel_username=get_bet3_panel_invitations[i].panel_username,
                    panel_full_name=get_bet3_panel_invitations[i].panel_full_name,
                    panel_response=get_bet3_panel_invitations[i].panel_response,
                    panel_response_date=get_bet3_panel_invitations[i].panel_response_date,
                    panel_attendance=get_bet3_panel_invitations[i].panel_attendance,
                    research_title_defense_date=get_bet3_panel_invitations[i].research_title_defense_date,
                    research_title_defense_start_time=get_bet3_panel_invitations[i].research_title_defense_start_time,
                    research_title_defense_end_time=get_bet3_panel_invitations[i].research_title_defense_end_time,
                    form_date_sent=get_bet3_panel_invitations[i].form_date_sent,
                    form_status=get_bet3_panel_invitations[i].form_status,
                    form=get_bet3_panel_invitations[i].form,
                    subject_teacher_username=get_bet3_panel_invitations[i].subject_teacher_username,
                    subject_teacher_full_name=get_bet3_panel_invitations[i].subject_teacher_full_name,
                    is_completed=get_bet3_panel_invitations[i].is_completed,
                )
                log_panel_invitation.save()
                i + 1

            for i in range(len(get_present_panel_members_title_defense)):
                log_research_title_defense_form = TitleDefenseFormLog(
                    student_leader_username=get_present_panel_members_title_defense[i].student_leader_username,
                    student_leader_full_name=get_present_panel_members_title_defense[i].student_leader_full_name,
                    course_major_abbr=get_present_panel_members_title_defense[i].course_major_abbr,
                    panel_username=get_present_panel_members_title_defense[i].panel_username,
                    panel_full_name=get_present_panel_members_title_defense[i].panel_full_name,
                    panel_attendance=get_present_panel_members_title_defense[i].panel_attendance,
                    is_panel_chairman=get_present_panel_members_title_defense[i].is_panel_chairman,
                    form_date=get_present_panel_members_title_defense[i].form_date,
                    form_status=get_present_panel_members_title_defense[i].form_status,
                    form=get_present_panel_members_title_defense[i].form,
                    subject_teacher_username=get_present_panel_members_title_defense[i].subject_teacher_username,
                    subject_teacher_full_name=get_present_panel_members_title_defense[i].subject_teacher_full_name,
                    defense_date=get_present_panel_members_title_defense[i].defense_date,
                    defense_start_time=get_present_panel_members_title_defense[i].defense_start_time,
                    defense_end_time=get_present_panel_members_title_defense[i].defense_end_time,
                )
                log_research_title_defense_form.save()
                i + 1

            get_student_leader_data.research_title_defense_date = ""
            get_student_leader_data.research_title_defense_start_time = ""
            get_student_leader_data.research_title_defense_end_time = ""
            get_student_leader_data.request_limit = 5
            get_student_leader_data.bet3_panel_invitation_status = ""
            get_student_leader_data.research_titles_status = ""
            get_student_leader_data.save()

            get_research_titles.delete()
            get_bet3_panel_invitations.delete()
            get_present_panel_members_title_defense.delete()
            updated_defense_schedule.delete()

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "date_today": today.strftime("%B %d, %Y"), "student_leader_full_name": student_leader_full_name, "response": "sweet re-defense"}

            return render(request, "subject-teacher-dashboard.html", context)

        else:
            print("not all deferred")
            pass

        get_student_title_defense_schedule.status = "Completed"
        get_student_title_defense_schedule.save()

        get_student_leader_data.title_defense_status = "completed"
        get_student_leader_data.request_limit = 5
        get_student_leader_data.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "date_today": today.strftime("%B %d, %Y"), 
            "response": "sweet title defense end"
            }

        return render(request, "subject-teacher-dashboard.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "research_titles": get_research_titles,
        "panel_members": get_panel_members,
        "present_panel_members": get_present_panel_members,
        "absent_panel_members": get_absent_panel_members,
        "present_panel_members_title_defense": get_present_panel_members_title_defense,
        "panel_chairman": get_panel_chairman,
        "pending_title_defense_vote": get_pending_title_defense_vote,
        "has_accepted_title": check_accepted_title,
        "research_title_accepted": get_research_title_accepted,
        "research_title_revise": get_research_title_revise,
        "research_title_all_deferred": all_deferred,
        "title_defense_completed": check_title_defense_completed,
        "pending_signature_response" : get_pending_signature_response,
        "start_voting" : get_start_voting,
    }

    return render(request, "subject-teacher-title-defense-day.html", context)


# Subject Teacher - Research Title Defense Day - Present Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDayPresent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = TitlePanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_panel_invitation_data.student_leader_username)
    except:
        return redirect("subject-teacher-dashboard")

    research_title_list = []
    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=get_panel_invitation_data.student_leader_username)

    for title in get_research_titles:
        research_title_list.append(title.research_title)

    print(research_title_list)

    for i in range(len(research_title_list)):
        create_title_voting_sheet = TitleVote(
            student_leader_username=get_panel_invitation_data.student_leader_username,
            student_leader_full_name=get_panel_invitation_data.student_leader_full_name,
            course_major_abbr=get_panel_invitation_data.course_major_abbr,
            research_title=research_title_list[i],
            panel_username=get_panel_invitation_data.panel_username,
            panel_full_name=get_panel_invitation_data.panel_full_name,
        )
        create_title_voting_sheet.save()
        i + 1

    get_panel_invitation_data.panel_attendance = "present"
    get_panel_invitation_data.save()

    save_title_defense_form = TitleDefenseForm(
        student_leader_username=get_panel_invitation_data.student_leader_username,
        student_leader_full_name=get_panel_invitation_data.student_leader_full_name,
        course_major_abbr=get_panel_invitation_data.course_major_abbr,
        panel_username=get_panel_invitation_data.panel_username,
        panel_full_name=get_panel_invitation_data.panel_full_name,
        panel_attendance="present",
        form_date=get_panel_invitation_data.research_title_defense_date,
        form="Research Title Defense",
        subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
        subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
        defense_date=get_student_leader_data.research_title_defense_date,
        defense_start_time=get_student_leader_data.research_title_defense_start_time,
        defense_end_time=get_student_leader_data.research_title_defense_end_time,
    )
    save_title_defense_form.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet present panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Absent Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDayAbsent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = TitlePanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    get_panel_invitation_data.panel_attendance = "absent"
    get_panel_invitation_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet absent panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Set Panel Chairman Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDaySetPanelChairman(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    save_panel_chairman = TitleDefenseForm.objects.get(id=id)
    save_panel_chairman.is_panel_chairman = True
    save_panel_chairman.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet panel chairman assigned",
        "panel_chairman_data": save_panel_chairman,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Start Voting
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDayStartVote(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # try:
    #     get_available_today_defense_schedule = DefenseSchedule.objects.all().filter(username = currently_loggedin_user.username, date = date_today, status = "Available")
    # except:
    #     pass

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    get_pending_signature_response = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_signature_response = 0)
    
    if get_pending_signature_response:
        
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,
            "student_leader_username": id,
            "response": "sweet panel esign incomplete"
        }

        return render(request, "subject-teacher-dashboard.html", context)


    get_done_signature_response = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_signature_response = 1)
    
    for i in range(len(get_done_signature_response)):
        get_done_signature_response[i].start_voting = True
        get_done_signature_response[i].save()
        i + 1
    
    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # try:
    #     get_available_today_defense_schedule = DefenseSchedule.objects.all().filter(username = currently_loggedin_user.username, date = date_today, status = "Available")
    # except:
    #     pass

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet start voting",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Close Voting
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherTitleDefenseDayCloseVote(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Subject Teacher - Get Subject Teacher Data
    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=today.strftime("%B %d, %Y"))

    get_pending_title_defense_vote = TitleDefenseForm.objects.all().filter(student_leader_username=id, form_status="")

    get_present_panel_members_title_defense = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")

    try:
        ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "student_leader_username": id,
            "response": "sweet already accepted title",
        }

        return render(request, "subject-teacher-dashboard.html", context)
    except:
        pass

    if get_pending_title_defense_vote:

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "student_leader_username": id,
            "response": "sweet panel voting pending",
        }

        return render(request, "subject-teacher-dashboard.html", context)

    #######################################################################################
    # Research Title 1 is Accepted
    try:
        if get_student_research_title_data[0].accepted > get_student_research_title_data[0].revise_title and get_student_research_title_data[0].accepted > get_student_research_title_data[0].deferred:

            update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
            update_research_title_data_0.status = "Title Defense - Accepted"
            update_research_title_data_0.title_defense_status = "Accepted"
            update_research_title_data_0.save()

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 2 is Accepted
    try:
        if get_student_research_title_data[1].accepted > get_student_research_title_data[1].revise_title and get_student_research_title_data[1].accepted > get_student_research_title_data[1].deferred:

            update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
            update_research_title_data_1.status = "Title Defense - Accepted"
            update_research_title_data_1.title_defense_status = "Accepted"
            update_research_title_data_1.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 3 is Accepted
    try:
        if get_student_research_title_data[2].accepted > get_student_research_title_data[2].revise_title and get_student_research_title_data[2].accepted > get_student_research_title_data[2].deferred:

            update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
            update_research_title_data_2.status = "Title Defense - Accepted"
            update_research_title_data_2.title_defense_status = "Accepted"
            update_research_title_data_2.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 4 is Accepted
    try:
        if get_student_research_title_data[3].accepted > get_student_research_title_data[3].revise_title and get_student_research_title_data[3].accepted > get_student_research_title_data[3].deferred:

            update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
            update_research_title_data_3.status = "Title Defense - Accepted"
            update_research_title_data_3.title_defense_status = "Accepted"
            update_research_title_data_3.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 5 is Accepted
    try:
        if get_student_research_title_data[4].accepted > get_student_research_title_data[4].revise_title and get_student_research_title_data[4].accepted > get_student_research_title_data[4].deferred:

            update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
            update_research_title_data_4.status = "Title Defense - Accepted"
            update_research_title_data_4.title_defense_status = "Accepted"
            update_research_title_data_4.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 1 is Revise Title
    try:
        if get_student_research_title_data[0].revise_title > get_student_research_title_data[0].accepted and get_student_research_title_data[0].revise_title > get_student_research_title_data[0].deferred:

            update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
            update_research_title_data_0.status = "Title Defense - Revise Title"
            update_research_title_data_0.title_defense_status = "Revise Title"
            update_research_title_data_0.save()

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 2 is Revise Title
    try:
        if get_student_research_title_data[1].revise_title > get_student_research_title_data[1].accepted and get_student_research_title_data[1].revise_title > get_student_research_title_data[1].deferred:

            update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
            update_research_title_data_1.status = "Title Defense - Revise Title"
            update_research_title_data_1.title_defense_status = "Revise Title"
            update_research_title_data_1.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 3 is Revise Title
    try:
        if get_student_research_title_data[2].revise_title > get_student_research_title_data[2].accepted and get_student_research_title_data[2].revise_title > get_student_research_title_data[2].deferred:

            update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
            update_research_title_data_2.status = "Title Defense - Revise Title"
            update_research_title_data_2.title_defense_status = "Revise Title"
            update_research_title_data_2.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 4 is Revise Title
    try:
        if get_student_research_title_data[3].revise_title > get_student_research_title_data[3].accepted and get_student_research_title_data[3].revise_title > get_student_research_title_data[3].deferred:

            update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
            update_research_title_data_3.status = "Title Defense - Revise Title"
            update_research_title_data_3.title_defense_status = "Revise Title"
            update_research_title_data_3.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                update_research_title_data_4.status = "Title Defense - Deferred"
                update_research_title_data_4.title_defense_status = "Deferred"
                update_research_title_data_4.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 5 is Revise Title
    try:
        if get_student_research_title_data[4].revise_title > get_student_research_title_data[4].accepted and get_student_research_title_data[4].revise_title > get_student_research_title_data[4].deferred:

            update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
            update_research_title_data_4.status = "Title Defense - Revise Title"
            update_research_title_data_4.title_defense_status = "Revise Title"
            update_research_title_data_4.save()

            try:
                update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                update_research_title_data_0.status = "Title Defense - Deferred"
                update_research_title_data_0.title_defense_status = "Deferred"
                update_research_title_data_0.save()
            except:
                pass

            try:
                update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                update_research_title_data_1.status = "Title Defense - Deferred"
                update_research_title_data_1.title_defense_status = "Deferred"
                update_research_title_data_1.save()
            except:
                pass

            try:
                update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                update_research_title_data_2.status = "Title Defense - Deferred"
                update_research_title_data_2.title_defense_status = "Deferred"
                update_research_title_data_2.save()
            except:
                pass

            try:
                update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                update_research_title_data_3.status = "Title Defense - Deferred"
                update_research_title_data_3.title_defense_status = "Deferred"
                update_research_title_data_3.save()
            except:
                pass

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet panel voting closed",
            }

            return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 1 is Deferred
    try:
        if get_student_research_title_data[0].deferred > get_student_research_title_data[0].accepted and get_student_research_title_data[0].deferred > get_student_research_title_data[0].revise_title:

            update_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
            update_research_title_data_0.status = "Title Defense - Deferred"
            update_research_title_data_0.title_defense_status = "Deferred"
            update_research_title_data_0.save()

    except:
        pass

    # Research Title 2 is Deferred
    try:
        if get_student_research_title_data[1].deferred > get_student_research_title_data[1].accepted and get_student_research_title_data[1].deferred > get_student_research_title_data[1].revise_title:

            update_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
            update_research_title_data_1.status = "Title Defense - Deferred"
            update_research_title_data_1.title_defense_status = "Deferred"
            update_research_title_data_1.save()

    except:
        pass

    # Research Title 3 is Deferred
    try:
        if get_student_research_title_data[2].deferred > get_student_research_title_data[2].accepted and get_student_research_title_data[2].deferred > get_student_research_title_data[2].revise_title:

            update_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
            update_research_title_data_2.status = "Title Defense - Deferred"
            update_research_title_data_2.title_defense_status = "Deferred"
            update_research_title_data_2.save()

    except:
        pass

    # Research Title 4 is Deferred
    try:
        if get_student_research_title_data[3].deferred > get_student_research_title_data[3].accepted and get_student_research_title_data[3].deferred > get_student_research_title_data[3].revise_title:

            update_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
            update_research_title_data_3.status = "Title Defense - Deferred"
            update_research_title_data_3.title_defense_status = "Deferred"
            update_research_title_data_3.save()

    except:
        pass

    # Research Title 5 is Deferred
    try:
        if get_student_research_title_data[4].deferred > get_student_research_title_data[4].accepted and get_student_research_title_data[4].deferred > get_student_research_title_data[4].revise_title:

            update_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
            update_research_title_data_4.status = "Title Defense - Deferred"
            update_research_title_data_4.title_defense_status = "Deferred"
            update_research_title_data_3.save()

    except:
        pass

    # Research Title 1 is undecided
    try:
        get_updated_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)
        if get_updated_student_research_title_data[0].status != "Title Defense - Deferred":
            if get_student_research_title_data[0].accepted == get_student_research_title_data[0].revise_title or get_student_research_title_data[0].accepted == get_student_research_title_data[0].deferred or get_student_research_title_data[0].revise_title == get_student_research_title_data[0].deferred:

                reset_research_title_data_0 = ResearchTitle.objects.get(id=get_student_research_title_data[0].id)
                reset_research_title_data_0.status = "Title Defense - Pending"
                reset_research_title_data_0.accepted = 0
                reset_research_title_data_0.deferred = 0
                reset_research_title_data_0.revise_title = 0
                reset_research_title_data_0.save()

                reset_research_title_defense_form_0 = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today)
                for i in range(len(reset_research_title_defense_form_0)):
                    reset_research_title_defense_form_0[i].form_status = ""
                    reset_research_title_defense_form_0[i].save()
                    i + 1

                reset_research_title_defense_vote_0 = TitleVote.objects.all().filter(student_leader_username=id, research_title=get_student_research_title_data[0].research_title)
                for i in range(len(reset_research_title_defense_vote_0)):
                    reset_research_title_defense_vote_0[i].panel_response = ""
                    reset_research_title_defense_vote_0[i].save()
                    i + 1

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "date_today": today.strftime("%B %d, %Y"),
                    "subject_teacher_data": get_subject_teacher_data,
                    "today_defense_schedule": get_today_defense_schedule,
                    "student_leader_username": id,
                    "response": "sweet panel vote again",
                    "tie_research_title": get_student_research_title_data[0].research_title,
                }

                return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 2 is undecided
    try:
        get_updated_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)
        if get_updated_student_research_title_data[1].status != "Title Defense - Deferred":
            if get_student_research_title_data[1].accepted == get_student_research_title_data[1].revise_title or get_student_research_title_data[1].accepted == get_student_research_title_data[1].deferred or get_student_research_title_data[1].revise_title == get_student_research_title_data[1].deferred:

                reset_research_title_data_1 = ResearchTitle.objects.get(id=get_student_research_title_data[1].id)
                reset_research_title_data_1.status = "Title Defense - Pending"
                reset_research_title_data_1.accepted = 0
                reset_research_title_data_1.deferred = 0
                reset_research_title_data_1.revise_title = 0
                reset_research_title_data_1.save()

                reset_research_title_defense_form_1 = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today)
                for i in range(len(reset_research_title_defense_form_1)):
                    reset_research_title_defense_form_1[i].form_status = ""
                    reset_research_title_defense_form_1[i].save()
                    i + 1

                reset_research_title_defense_vote_1 = TitleVote.objects.all().filter(student_leader_username=id, research_title=get_student_research_title_data[1].research_title)
                for i in range(len(reset_research_title_defense_vote_1)):
                    reset_research_title_defense_vote_1[i].panel_response = ""
                    reset_research_title_defense_vote_1[i].save()
                    i + 1

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "date_today": today.strftime("%B %d, %Y"),
                    "subject_teacher_data": get_subject_teacher_data,
                    "today_defense_schedule": get_today_defense_schedule,
                    "student_leader_username": id,
                    "response": "sweet panel vote again",
                    "tie_research_title": get_student_research_title_data[1].research_title,
                }

                return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 3 is undecided
    try:
        get_updated_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)
        if get_updated_student_research_title_data[2].status != "Title Defense - Deferred":
            if get_student_research_title_data[2].accepted == get_student_research_title_data[2].revise_title or get_student_research_title_data[2].accepted == get_student_research_title_data[2].deferred or get_student_research_title_data[2].revise_title == get_student_research_title_data[2].deferred:

                reset_research_title_data_2 = ResearchTitle.objects.get(id=get_student_research_title_data[2].id)
                reset_research_title_data_2.status = "Title Defense - Pending"
                reset_research_title_data_2.accepted = 0
                reset_research_title_data_2.deferred = 0
                reset_research_title_data_2.revise_title = 0
                reset_research_title_data_2.save()

                reset_research_title_defense_form_2 = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today)
                for i in range(len(reset_research_title_defense_form_2)):
                    reset_research_title_defense_form_2[i].form_status = ""
                    reset_research_title_defense_form_2[i].save()
                    i + 1

                reset_research_title_defense_vote_2 = TitleVote.objects.all().filter(student_leader_username=id, research_title=get_student_research_title_data[2].research_title)
                for i in range(len(reset_research_title_defense_vote_2)):
                    reset_research_title_defense_vote_2[i].panel_response = ""
                    reset_research_title_defense_vote_2[i].save()
                    i + 1

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "date_today": today.strftime("%B %d, %Y"),
                    "subject_teacher_data": get_subject_teacher_data,
                    "today_defense_schedule": get_today_defense_schedule,
                    "student_leader_username": id,
                    "response": "sweet panel vote again",
                    "tie_research_title": get_student_research_title_data[2].research_title,
                }

                return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 4 is undecided
    try:
        get_updated_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)
        if get_updated_student_research_title_data[3].status != "Title Defense - Deferred":
            if get_student_research_title_data[3].accepted == get_student_research_title_data[3].revise_title or get_student_research_title_data[3].accepted == get_student_research_title_data[3].deferred or get_student_research_title_data[3].revise_title == get_student_research_title_data[3].deferred:

                reset_research_title_data_3 = ResearchTitle.objects.get(id=get_student_research_title_data[3].id)
                reset_research_title_data_3.status = "Title Defense - Pending"
                reset_research_title_data_3.accepted = 0
                reset_research_title_data_3.deferred = 0
                reset_research_title_data_3.revise_title = 0
                reset_research_title_data_3.save()

                reset_research_title_defense_form_3 = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today)
                for i in range(len(reset_research_title_defense_form_3)):
                    reset_research_title_defense_form_3[i].form_status = ""
                    reset_research_title_defense_form_3[i].save()
                    i + 1

                reset_research_title_defense_vote_3 = TitleVote.objects.all().filter(student_leader_username=id, research_title=get_student_research_title_data[3].research_title)
                for i in range(len(reset_research_title_defense_vote_3)):
                    reset_research_title_defense_vote_3[i].panel_response = ""
                    reset_research_title_defense_vote_3[i].save()
                    i + 1

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "date_today": today.strftime("%B %d, %Y"),
                    "subject_teacher_data": get_subject_teacher_data,
                    "today_defense_schedule": get_today_defense_schedule,
                    "student_leader_username": id,
                    "response": "sweet panel vote again",
                    "tie_research_title": get_student_research_title_data[3].research_title,
                }

                return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    # Research Title 5 is undecided
    try:
        get_updated_student_research_title_data = ResearchTitle.objects.all().filter(student_leader_username=id)
        if get_updated_student_research_title_data[4].status != "Title Defense - Deferred":
            if get_student_research_title_data[4].accepted == get_student_research_title_data[4].revise_title or get_student_research_title_data[4].accepted == get_student_research_title_data[4].deferred or get_student_research_title_data[4].revise_title == get_student_research_title_data[4].deferred:

                reset_research_title_data_4 = ResearchTitle.objects.get(id=get_student_research_title_data[4].id)
                reset_research_title_data_4.status = "Title Defense - Pending"
                reset_research_title_data_4.accepted = 0
                reset_research_title_data_4.deferred = 0
                reset_research_title_data_4.revise_title = 0
                reset_research_title_data_4.save()

                reset_research_title_defense_form_4 = TitleDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today)
                for i in range(len(reset_research_title_defense_form_4)):
                    reset_research_title_defense_form_4[i].form_status = ""
                    reset_research_title_defense_form_4[i].save()
                    i + 1

                reset_research_title_defense_vote_4 = TitleVote.objects.all().filter(student_leader_username=id, research_title=get_student_research_title_data[4].research_title)
                for i in range(len(reset_research_title_defense_vote_4)):
                    reset_research_title_defense_vote_4[i].panel_response = ""
                    reset_research_title_defense_vote_4[i].save()
                    i + 1

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                    "date_today": today.strftime("%B %d, %Y"),
                    "subject_teacher_data": get_subject_teacher_data,
                    "today_defense_schedule": get_today_defense_schedule,
                    "student_leader_username": id,
                    "response": "sweet panel vote again",
                    "tie_research_title": get_student_research_title_data[4].research_title,
                }

                return render(request, "subject-teacher-dashboard.html", context)

    except:
        pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet all titles deferred",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDay(request, id):

    print(request.user)

    # ----- Topbar Process -----
    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    print("Subject Teacher: ", currently_loggedin_user_full_name, "-", currently_loggedin_user_account)
    # ----- Topbar Process -----

    # ----- Student Leader Data -----
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
        print("Student Leader: ", get_student_leader_data.username)
    except:
        return redirect("subject-teacher-dashboard")

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."
    print("Student Leader Full Name: ", student_leader_full_name)
    # ----- Student Leader Data -----


    # ----- Validation ------

    # If Student Defense Schedule and Date Today is not the same
    if get_student_leader_data.research_proposal_defense_date != date_today:
        return redirect("subject-teacher-dashboard")
    
     # ----- Validation ------

    # ----- Fetch Data -----
    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id) # Get all the group members

    get_panel_members  = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="")

    get_present_panel_members = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present")
    get_pending_proposal_defense = ProposalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present", is_completed = False)

    get_absent_panel_members = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="absent")
    
    get_bet3_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=id)

    get_proposal_defense_present_panel = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")

    get_present_panel_members_proposal_defense = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")

    get_start_critique = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_critique = 1)

    get_end_critique = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, end_critique = 1)

    check_pending = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, end_critique = 1)
    
    check_pending_critique = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, critique_sign_response = False)

    get_start_voting = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1)

    get_end_voting = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, end_voting = 1)

    check_pending_vote = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, proposal_defense_response = "")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        print("pass")
        return redirect("subject-teacher-dashboard")
    
    try:
        get_student_proposal_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, form="Research Proposal Defense", date=date_today, status="Reserved")
    except:
        pass
    
    try:
        get_panel_chairman = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, panel_attendance="present", is_panel_chairman=1)
        print("Panel Chairman: ", get_panel_chairman.panel_full_name)
    except:
        get_panel_chairman = None

    try:
        get_pending_panel_chairman_signature_response = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, panel_chairman_signature_response = 1)
    except:
        get_pending_panel_chairman_signature_response = 0
    
    try:
        get_done_pc_sign = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_pc_sign = None

    try:
        get_done_p_sign = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_p_sign = None


    all_pending_panel_signature_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, panel_signature_response = False)
    
     # ----- Fetch Data -----

    if not get_panel_members:
        if get_present_panel_members.count() < 3:
            print("Re Schedule")

            get_student_proposal_defense_schedule.status = "Reschedule"
            get_student_proposal_defense_schedule.save()

            # Get Updated Defense Schedule
            try:
                updated_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, form="Research Proposal Defense", date=date_today, status="Reschedule")

                log_defense_schedule = DefenseScheduleLog(
                    username=updated_defense_schedule.username, 
                    name=updated_defense_schedule.name, 
                    student_leader_username=updated_defense_schedule.student_leader_username, 
                    student_leader_name=updated_defense_schedule.student_leader_name, 
                    course=updated_defense_schedule.course, 
                    form=updated_defense_schedule.form, 
                    date=updated_defense_schedule.date, 
                    start_time=updated_defense_schedule.start_time, 
                    end_time=updated_defense_schedule.end_time, 
                    status=updated_defense_schedule.status
                )

                log_defense_schedule.save()
                print("Subject Teacher - Defense Schedule Log - Success")

            except:
                updated_defense_schedule = None

            for i in range(len(get_bet3_panel_invitations)):
                log_panel_invitation = ProposalPanelInvitationLog(
                    student_leader_username=get_bet3_panel_invitations[i].student_leader_username,
                    student_leader_full_name=get_bet3_panel_invitations[i].student_leader_full_name,
                    course_major_abbr=get_bet3_panel_invitations[i].course_major_abbr,
                    dit_head_username=get_bet3_panel_invitations[i].dit_head_username,
                    dit_head_full_name=get_bet3_panel_invitations[i].dit_head_full_name,
                    dit_head_response=get_bet3_panel_invitations[i].dit_head_response,
                    dit_head_response_date=get_bet3_panel_invitations[i].dit_head_response_date,
                    panel_username=get_bet3_panel_invitations[i].panel_username,
                    panel_full_name=get_bet3_panel_invitations[i].panel_full_name,
                    panel_response=get_bet3_panel_invitations[i].panel_response,
                    panel_response_date=get_bet3_panel_invitations[i].panel_response_date,
                    panel_attendance=get_bet3_panel_invitations[i].panel_attendance+"-reschedule",
                    research_proposal_defense_date=get_bet3_panel_invitations[i].research_proposal_defense_date,
                    research_proposal_defense_start_time=get_bet3_panel_invitations[i].research_proposal_defense_start_time,
                    research_proposal_defense_end_time=get_bet3_panel_invitations[i].research_proposal_defense_end_time,
                    form_date_sent=get_bet3_panel_invitations[i].form_date_sent,
                    form_status=get_bet3_panel_invitations[i].form_status,
                    form=get_bet3_panel_invitations[i].form,
                    subject_teacher_username=get_bet3_panel_invitations[i].subject_teacher_username,
                    subject_teacher_full_name=get_bet3_panel_invitations[i].subject_teacher_full_name,
                    is_completed=get_bet3_panel_invitations[i].is_completed,
                )
                log_panel_invitation.save()
                i + 1
                print("Subject Teacher - Proposal Defense Panel Invitation Log - Success")

            for i in range(len(get_proposal_defense_present_panel)):
                log_research_proposal_defense = ProposalDefenseFormLog(
                    student_leader_username=get_proposal_defense_present_panel[i].student_leader_username,
                    student_leader_full_name=get_proposal_defense_present_panel[i].student_leader_full_name,
                    course_major_abbr=get_proposal_defense_present_panel[i].course_major_abbr,
                    panel_username=get_proposal_defense_present_panel[i].panel_username,
                    panel_full_name=get_proposal_defense_present_panel[i].panel_full_name,
                    panel_attendance=get_proposal_defense_present_panel[i].panel_attendance,
                    is_panel_chairman=get_proposal_defense_present_panel[i].is_panel_chairman,
                    form_date=get_proposal_defense_present_panel[i].form_date,
                    form_status=get_proposal_defense_present_panel[i].form_status,
                    form=get_proposal_defense_present_panel[i].form,
                    subject_teacher_username=get_proposal_defense_present_panel[i].subject_teacher_username,
                    subject_teacher_full_name=get_proposal_defense_present_panel[i].subject_teacher_full_name,
                    defense_date=get_proposal_defense_present_panel[i].defense_date,
                    defense_start_time=get_proposal_defense_present_panel[i].defense_start_time,
                    defense_end_time=get_proposal_defense_present_panel[i].defense_end_time,
                )
                log_research_proposal_defense.save()
                i + 1
                print("Subject Teacher - Proposal Defese Form Log - Success")

            get_student_leader_data.research_proposal_defense_date = ""
            get_student_leader_data.research_proposal_defense_start_time = ""
            get_student_leader_data.research_proposal_defense_end_time = ""
            get_student_leader_data.request_limit = 5
            get_student_leader_data.bet3_proposal_defense_panel_invitation_status = ""
            get_student_leader_data.save()

            get_bet3_panel_invitations.delete()
            get_proposal_defense_present_panel.delete()
            updated_defense_schedule.delete()

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "date_today": today.strftime("%B %d, %Y"), 
                "student_leader_full_name": student_leader_full_name, 

                "response": "sweet re-defense incomplete panel"}

            return render(request, "subject-teacher-dashboard.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,

        "group_members": get_group_members,

        "accepted_research_title": get_accepted_research_title,

        "panel_members": get_panel_members,

        "present_panel_members": get_present_panel_members,
        "absent_panel_members": get_absent_panel_members,

        "present_panel_members_proposal_defense": get_present_panel_members_proposal_defense,
        "panel_chairman": get_panel_chairman,
        "pending_signature_response" : get_pending_panel_chairman_signature_response,
        "start_critique" : get_start_critique,
        "end_critique" : get_end_critique,
        "check_pending_critique": check_pending_critique,
        "start_voting": get_start_voting,
        "end_voting": get_end_voting,
        "done_panel_chairman_sign": get_done_pc_sign,
        "all_pending_panel_signature_response": all_pending_panel_signature_response,
        "pending_proposal_defense": get_pending_proposal_defense,
    }

    return render(request, "subject-teacher-bet3-proposal-defense-day.html", context)


# Subject Teacher - Research Proposal Defense Day - Present Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefensePresent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = ProposalPanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_panel_invitation_data.student_leader_username)
    except:
        return redirect("subject-teacher-dashboard")

    get_panel_invitation_data.panel_attendance = "present"
    get_panel_invitation_data.save()

    save_proposal_defense_form = ProposalDefenseForm(
        student_leader_username=get_panel_invitation_data.student_leader_username,
        student_leader_full_name=get_panel_invitation_data.student_leader_full_name,
        course_major_abbr=get_panel_invitation_data.course_major_abbr,

        panel_username=get_panel_invitation_data.panel_username,
        panel_full_name=get_panel_invitation_data.panel_full_name,
        panel_attendance="present",

        form_date=get_panel_invitation_data.research_proposal_defense_date,
        form="Research Proposal Defense",

        subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
        subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,

        defense_date=get_student_leader_data.research_proposal_defense_date,
        defense_start_time=get_student_leader_data.research_proposal_defense_start_time,
        defense_end_time=get_student_leader_data.research_proposal_defense_end_time,
    )
    save_proposal_defense_form.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet proposal defense present panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Absent Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseAbsent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = ProposalPanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    get_panel_invitation_data.panel_attendance = "absent"
    get_panel_invitation_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet proposal defense absent panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Title Defense Day - Set Panel Chairman Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDaySetPanelChairman(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    save_panel_chairman = ProposalDefenseForm.objects.get(id=id)
    save_panel_chairman.is_panel_chairman = True
    save_panel_chairman.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet proposal defense panel chairman assigned",
        "panel_chairman_data": save_panel_chairman,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day - Start Critique
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDayStartCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        return redirect("subject-teacher-dashboard")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    try:
        get_pending_signature_response = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_chairman_signature_response = 0)
    
        if get_pending_signature_response:
            
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": today.strftime("%B %d, %Y"),
                "subject_teacher_data": get_subject_teacher_data,
                "today_defense_schedule": get_today_defense_schedule,
                "completed_today_defense_schedule": get_completed_today_defense_schedule,
                "student_leader_username": id,
                "response": "sweet proposal defense panel esign incomplete"
            }

            return render(request, "subject-teacher-dashboard.html", context)
    except:
        pass


    get_done_signature_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)

    for i in range(len(get_done_signature_response)):
        get_done_signature_response[i].start_critique = True
        get_done_signature_response[i].save()

        save_critique = ProposalDefenseCritique(
            student_leader_username = get_done_signature_response[i].student_leader_username,
            student_leader_full_name = get_done_signature_response[i].student_leader_full_name,
            course_major_abbr = get_done_signature_response[i].course_major_abbr,

            panel_username = get_done_signature_response[i].panel_username,
            panel_full_name = get_done_signature_response[i].panel_full_name,
            panel_attendance = get_done_signature_response[i].panel_attendance,
            is_panel_chairman = get_done_signature_response[i].is_panel_chairman,

            form_date = date_today,

            form_status = get_done_signature_response[i].form_status,
            form = "Critique Form",

            subject_teacher_username = get_done_signature_response[i].subject_teacher_username,
            subject_teacher_full_name = get_done_signature_response[i].subject_teacher_full_name,

            defense_date = get_done_signature_response[i].defense_date,
            defense_start_time = get_done_signature_response[i].defense_start_time,
            defense_end_time = get_done_signature_response[i].defense_end_time,
            
            research_title = get_accepted_research_title.research_title
            )
        save_critique.save()

        i + 1

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet proposal defense start critique",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day - End Critique
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDayEndCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    # try:
    #     get_pending_signature_response = ProposalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, panel_chairman_signature_response = 0)
    
    #     if get_pending_signature_response:
            
    #         context = {
    #             "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
    #             "date_today": today.strftime("%B %d, %Y"),
    #             "subject_teacher_data": get_subject_teacher_data,
    #             "today_defense_schedule": get_today_defense_schedule,
    #             "completed_today_defense_schedule": get_completed_today_defense_schedule,
    #             "student_leader_username": id,
    #             "response": "sweet proposal defense panel esign incomplete"
    #         }

    #         return render(request, "subject-teacher-dashboard.html", context)
    # except:
    #     pass


    get_done_signature_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)
    
    for i in range(len(get_done_signature_response)):
        get_done_signature_response[i].end_critique = True
        get_done_signature_response[i].save()
        i + 1
    
    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet proposal defense end critique",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day - Start Voting
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDayStartVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    get_done_signature_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)

    for i in range(len(get_done_signature_response)):
        get_done_signature_response[i].start_voting = True
        get_done_signature_response[i].save()

        i + 1

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet proposal defense start voting",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day - End Voting
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDayEndVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    
    get_accepted_panel_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, proposal_defense_response = "Accepted with Revision")
    get_deferred_panel_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, proposal_defense_response = "Deferred with Revision")
    get_not_accepted_panel_response = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, proposal_defense_response = "Not Accepted")

    get_student_proposal_defense_form = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)
    get_student_proposal_defense_critique = ProposalDefenseCritique.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)

    accepted_with_revision_count = get_accepted_panel_response.count()
    deferred_with_revision_count = get_deferred_panel_response.count()
    not_accepted_count = get_not_accepted_panel_response.count()

    print("Accepted with Revision: ", accepted_with_revision_count)
    print("Deferred with Revision: ", deferred_with_revision_count)
    print("Not Accepted: ", not_accepted_count)

    if int(accepted_with_revision_count) >= 3:
        print("Accepted with Revision")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Accepted with Revision"
            get_student_proposal_defense_form[i].end_voting = True
            get_student_proposal_defense_form[i].save()
            i + 1

        ProposalDefenseCritique.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username).update(form_status = "completed")
        ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(proposal_defense_status = "Accepted with Revision", status = "Proposal Defense - Accepted with Revision")
    
    elif int(deferred_with_revision_count) >= 3:
        print("Deferred with Revision - Redefense")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Deferred with Revision"
            get_student_proposal_defense_form[i].end_voting = True
            get_student_proposal_defense_form[i].save()
            i + 1
        
        ProposalDefenseCritique.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username).update(form_status = "completed")
        ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(proposal_defense_status = "Deferred with Revision", status = "Proposal Defense - Deferred with Revision")
    
    elif int(not_accepted_count) >= 3:
        print("Not Accepted")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Not Accepted"
            get_student_proposal_defense_form[i].save()
            i + 1
        
        ProposalDefenseCritique.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username).update(form_status = "completed")
        ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(proposal_defense_status = "Not Accepted", status = "Proposal Defense - Not Accepted")

    elif accepted_with_revision_count == deferred_with_revision_count or accepted_with_revision_count == not_accepted_count or deferred_with_revision_count == not_accepted_count:
        print("Tie - re-vote")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].proposal_defense_response = None
            get_student_proposal_defense_form[i].panel_chairman_signature_response = False
            get_student_proposal_defense_form[i].panel_chairman_signature_attach = False
            get_student_proposal_defense_form[i].panel_signature_response = False
            get_student_proposal_defense_form[i].panel_signature_attach = False
            get_student_proposal_defense_form[i].save()
            i + 1
        
        context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet proposal defense vote tie",
        }

        return render(request, "subject-teacher-dashboard.html", context)
    

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet proposal defense end voting",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Day - End Defense
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3ProposalDefenseDayEndDefense(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")


    try:
        get_student_research_title = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        return redirect("subject-teacher-dashboard")
    
    if get_student_research_title.proposal_defense_status == "Accepted with Revision":
        DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Proposal Defense").update(status = "Completed")
        StudentLeader.objects.filter(username=id).update(bet3_proposal_defense_status = "completed", request_limit = 5)
        ProposalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present").update(is_completed = True)
        
        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet proposal defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)

    elif get_student_research_title.proposal_defense_status == "Deferred with Revision":
        get_student_proposal_panel_invitation = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present")
        get_student_proposal_defense_schedule = DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Proposal Defense")
        get_student_proposal_defense_forms = ProposalDefenseForm.objects.all().filter(student_leader_username=id, subject_teacher_username = request.user, defense_date=date_today)

        # Proposal Panel Invitation Logs
        for i in range (len(get_student_proposal_panel_invitation)):
            log_proposal_panel_invitation = ProposalPanelInvitationLog(
                student_leader_username = get_student_proposal_panel_invitation[i].student_leader_username,
                student_leader_full_name = get_student_proposal_panel_invitation[i].student_leader_full_name,
                course_major_abbr = get_student_proposal_panel_invitation[i].course_major_abbr,
                
                dit_head_username= get_student_proposal_panel_invitation[i].dit_head_username,
                dit_head_full_name = get_student_proposal_panel_invitation[i].dit_head_full_name,
                dit_head_response = get_student_proposal_panel_invitation[i].dit_head_response,
                dit_head_response_date = get_student_proposal_panel_invitation[i].dit_head_response_date,
                dit_head_signature = get_student_proposal_panel_invitation[i].dit_head_signature,

                panel_username = get_student_proposal_panel_invitation[i].panel_username,
                panel_full_name = get_student_proposal_panel_invitation[i].panel_full_name,
                panel_response = get_student_proposal_panel_invitation[i].panel_response,
                panel_response_date = get_student_proposal_panel_invitation[i].panel_response_date,
                panel_signature = get_student_proposal_panel_invitation[i].panel_signature,
                panel_attendance = get_student_proposal_panel_invitation[i].panel_attendance,

                research_proposal_defense_date = get_student_proposal_panel_invitation[i].research_proposal_defense_date,
                research_proposal_defense_start_time = get_student_proposal_panel_invitation[i].research_proposal_defense_start_time,
                research_proposal_defense_end_time = get_student_proposal_panel_invitation[i].research_proposal_defense_end_time,

                form_date_sent = get_student_proposal_panel_invitation[i].form_date_sent,

                form_status = get_student_proposal_panel_invitation[i].form_status,
                form = get_student_proposal_panel_invitation[i].form,

                subject_teacher_username = get_student_proposal_panel_invitation[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_panel_invitation[i].subject_teacher_full_name,

                is_completed = get_student_proposal_panel_invitation[i].is_completed,
            )
            log_proposal_panel_invitation.save()
            i + 1
        print("Proposal Panel Invitation - Log - Successfully")
        
        # Proposal Defense Schedule Logs
        for i in range (len(get_student_proposal_defense_schedule)):
            log_proposal_defense_schedule = DefenseScheduleLog(
                username = get_student_proposal_defense_schedule[i].username,
                name = get_student_proposal_defense_schedule[i].name,
                student_leader_username = get_student_proposal_defense_schedule[i].student_leader_username,
                student_leader_name = get_student_proposal_defense_schedule[i].student_leader_name,
                course = get_student_proposal_defense_schedule[i].course,
                form = get_student_proposal_defense_schedule[i].form,
                date = get_student_proposal_defense_schedule[i].date,
                start_time = get_student_proposal_defense_schedule[i].start_time,
                end_time = get_student_proposal_defense_schedule[i].end_time,
                status = "Re-Defense",
            )
            log_proposal_defense_schedule.save()
            i + 1
        print("Proposal Defense Schedule - Log - Successfully")

        for i in range (len(get_student_proposal_defense_forms)):
            log_proposal_defense_form = ProposalDefenseFormLog(
                student_leader_username = get_student_proposal_defense_forms[i].student_leader_username ,
                student_leader_full_name = get_student_proposal_defense_forms[i].student_leader_full_name ,
                course_major_abbr = get_student_proposal_defense_forms[i].course_major_abbr,

                panel_username = get_student_proposal_defense_forms[i].panel_username ,
                panel_full_name = get_student_proposal_defense_forms[i].panel_full_name ,
                panel_attendance = get_student_proposal_defense_forms[i].panel_attendance ,
                panel_signature_response = get_student_proposal_defense_forms[i].panel_signature_response ,
                panel_signature_attach = get_student_proposal_defense_forms[i].panel_signature_attach ,

                is_panel_chairman = get_student_proposal_defense_forms[i].is_panel_chairman ,
                panel_chairman_signature_response = get_student_proposal_defense_forms[i].panel_chairman_signature_response ,
                panel_chairman_signature_attach = get_student_proposal_defense_forms[i].panel_chairman_signature_attach ,

                form_date = get_student_proposal_defense_forms[i].form_date ,

                start_critique = get_student_proposal_defense_forms[i].start_critique ,
                end_critique = get_student_proposal_defense_forms[i].end_critique ,

                start_voting = get_student_proposal_defense_forms[i].start_voting ,
                end_voting = get_student_proposal_defense_forms[i].end_voting ,

                form_status = get_student_proposal_defense_forms[i].form_status ,
                form = get_student_proposal_defense_forms[i].form ,

                subject_teacher_username = get_student_proposal_defense_forms[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_defense_forms[i].subject_teacher_full_name,

                defense_date = get_student_proposal_defense_forms[i].defense_date,
                defense_start_time = get_student_proposal_defense_forms[i].defense_start_time,
                defense_end_time = get_student_proposal_defense_forms[i].defense_end_time,

                critique_sign_response = get_student_proposal_defense_forms[i].critique_sign_response ,
                proposal_defense_response = get_student_proposal_defense_forms[i].proposal_defense_response,
            )
            log_proposal_defense_form.save()
            i + 1
        print("Proposal Defense Forms - Log - Successfully")

        get_student_proposal_panel_invitation.delete()
        get_student_proposal_defense_schedule.delete()
        get_student_proposal_defense_forms.delete()
        StudentLeader.objects.filter(username=id).update(bet3_proposal_defense_panel_invitation_status = "", request_limit = 5, research_proposal_defense_date ="", research_proposal_defense_start_time = "", research_proposal_defense_end_time = "")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet proposal defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)

    elif get_student_research_title.proposal_defense_status == "Not Accepted":
        get_student_research_titles = ResearchTitle.objects.all().filter(student_leader_username=id)
        get_student_title_panel_invitation = TitlePanelInvitation.objects.all().filter(student_leader_username=id)
        get_student_title_defense_schedule = DefenseSchedule.objects.all().filter(student_leader_username=id, form = "Research Title Defense")
        get_student_title_defense_form = TitleDefenseForm.objects.all().filter(student_leader_username=id)
        get_student_proposal_panel_invitation = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present")
        get_student_proposal_defense_schedule = DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Proposal Defense")
        get_student_proposal_defense_forms = ProposalDefenseForm.objects.all().filter(student_leader_username=id, subject_teacher_username = request.user, defense_date=date_today)

        # Research Title Log
        for i in range(len(get_student_research_titles)):
            log_research_titles = ResearchTitleLog(
                research_title = get_student_research_titles[i].research_title ,

                course = get_student_research_titles[i].course ,
                major = get_student_research_titles[i].major ,
                course_major_abbr = get_student_research_titles[i].course_major_abbr ,

                student_leader_username = get_student_research_titles[i].student_leader_username ,
                student_leader_name = get_student_research_titles[i].student_leader_name ,

                status = get_student_research_titles[i].status ,
                date_submitted = get_student_research_titles[i].date_submitted ,

                accepted = get_student_research_titles[i].accepted ,
                deferred = get_student_research_titles[i].deferred ,
                revise_title = get_student_research_titles[i].revise_title ,
                suggested_title =  get_student_research_titles[i].suggested_title ,
                old_research_title = get_student_research_titles[i].old_research_title ,

                defense_date = get_student_research_titles[i].defense_date ,

                title_defense_status = get_student_research_titles[i].title_defense_status ,
                proposal_defense_status = get_student_research_titles[i].proposal_defense_status ,
            )
            log_research_titles.save()
            i + 1
        print("Research Title - Log - Successfully")

        # Title Panel Invitation Log
        for i in range(len(get_student_title_panel_invitation)):
            log_student_title_panel_invitation = TitlePanelInvitationLog(
                student_leader_username = get_student_title_panel_invitation[i].student_leader_username,
                student_leader_full_name = get_student_title_panel_invitation[i].student_leader_full_name,
                course_major_abbr = get_student_title_panel_invitation[i].course_major_abbr,
                
                dit_head_username= get_student_title_panel_invitation[i].dit_head_username,
                dit_head_full_name = get_student_title_panel_invitation[i].dit_head_full_name,
                dit_head_response = get_student_title_panel_invitation[i].dit_head_response,
                dit_head_response_date = get_student_title_panel_invitation[i].dit_head_response_date,
                dit_head_signature = get_student_title_panel_invitation[i].dit_head_signature,

                panel_username = get_student_title_panel_invitation[i].panel_username,
                panel_full_name = get_student_title_panel_invitation[i].panel_full_name,
                panel_response = get_student_title_panel_invitation[i].panel_response,
                panel_response_date = get_student_title_panel_invitation[i].panel_response_date,
                panel_signature = get_student_title_panel_invitation[i].panel_signature,
                panel_attendance = get_student_title_panel_invitation[i].panel_attendance,

                research_title_defense_date = get_student_title_panel_invitation[i].research_title_defense_date,
                research_title_defense_start_time = get_student_title_panel_invitation[i].research_title_defense_start_time,
                research_title_defense_end_time = get_student_title_panel_invitation[i].research_title_defense_end_time,

                form_date_sent = get_student_title_panel_invitation[i].form_date_sent,

                form_status = get_student_title_panel_invitation[i].form_status,
                form = get_student_title_panel_invitation[i].form,

                subject_teacher_username = get_student_title_panel_invitation[i].subject_teacher_username,
                subject_teacher_full_name = get_student_title_panel_invitation[i].subject_teacher_full_name,

                is_completed = get_student_title_panel_invitation[i].is_completed,
            )
            log_student_title_panel_invitation.save()
            i + 1
        print("Title Panel Invitation - Log - Successfully")

        # Title Defense Schedule Log
        for i in range(len(get_student_title_defense_schedule)):
            log_title_defense_schedule = DefenseScheduleLog(
                username = get_student_title_defense_schedule[i].username,
                name = get_student_title_defense_schedule[i].name,
                student_leader_username = get_student_title_defense_schedule[i].student_leader_username,
                student_leader_name = get_student_title_defense_schedule[i].student_leader_name,
                course = get_student_title_defense_schedule[i].course,
                form = get_student_title_defense_schedule[i].form,
                date = get_student_title_defense_schedule[i].date,
                start_time = get_student_title_defense_schedule[i].start_time,
                end_time = get_student_title_defense_schedule[i].end_time,
                status = get_student_title_defense_schedule[i].status,
            )
            log_title_defense_schedule.save()
            i + 1
        print("Title Defense Schedule - Log - Successfully")

        # Title Defense Form Log
        for i in range(len(get_student_title_defense_form)):
            log_title_defense_form = TitleDefenseFormLog(
                student_leader_username = get_student_title_defense_form[i].student_leader_username,
                student_leader_full_name = get_student_title_defense_form[i].student_leader_full_name,
                course_major_abbr = get_student_title_defense_form[i].course_major_abbr,

                panel_username = get_student_title_defense_form[i].panel_username,
                panel_full_name = get_student_title_defense_form[i].panel_full_name,
                panel_attendance = get_student_title_defense_form[i].panel_attendance,
                is_panel_chairman = get_student_title_defense_form[i].is_panel_chairman,
                panel_signature_response = get_student_title_defense_form[i].panel_signature_response,
                panel_signature_attach = get_student_title_defense_form[i].panel_signature_attach,

                form_date = get_student_title_defense_form[i].form_date,

                form_status = get_student_title_defense_form[i].form_status,
                form = get_student_title_defense_form[i].form,

                subject_teacher_username = get_student_title_defense_form[i].subject_teacher_username,
                subject_teacher_full_name = get_student_title_defense_form[i].subject_teacher_full_name,
                defense_date = get_student_title_defense_form[i].defense_date,
                defense_start_time = get_student_title_defense_form[i].defense_start_time,
                defense_end_time = get_student_title_defense_form[i].defense_end_time,
            )
            log_title_defense_form.save()
            i + 1
        print("Title Defense Form - Log - Successfully")

        # Proposal Panel Invitation Logs
        for i in range (len(get_student_proposal_panel_invitation)):
            log_proposal_panel_invitation = ProposalPanelInvitationLog(
                student_leader_username = get_student_proposal_panel_invitation[i].student_leader_username,
                student_leader_full_name = get_student_proposal_panel_invitation[i].student_leader_full_name,
                course_major_abbr = get_student_proposal_panel_invitation[i].course_major_abbr,
                
                dit_head_username= get_student_proposal_panel_invitation[i].dit_head_username,
                dit_head_full_name = get_student_proposal_panel_invitation[i].dit_head_full_name,
                dit_head_response = get_student_proposal_panel_invitation[i].dit_head_response,
                dit_head_response_date = get_student_proposal_panel_invitation[i].dit_head_response_date,
                dit_head_signature = get_student_proposal_panel_invitation[i].dit_head_signature,

                panel_username = get_student_proposal_panel_invitation[i].panel_username,
                panel_full_name = get_student_proposal_panel_invitation[i].panel_full_name,
                panel_response = get_student_proposal_panel_invitation[i].panel_response,
                panel_response_date = get_student_proposal_panel_invitation[i].panel_response_date,
                panel_signature = get_student_proposal_panel_invitation[i].panel_signature,
                panel_attendance = get_student_proposal_panel_invitation[i].panel_attendance,

                research_proposal_defense_date = get_student_proposal_panel_invitation[i].research_proposal_defense_date,
                research_proposal_defense_start_time = get_student_proposal_panel_invitation[i].research_proposal_defense_start_time,
                research_proposal_defense_end_time = get_student_proposal_panel_invitation[i].research_proposal_defense_end_time,

                form_date_sent = get_student_proposal_panel_invitation[i].form_date_sent,

                form_status = get_student_proposal_panel_invitation[i].form_status,
                form = get_student_proposal_panel_invitation[i].form,

                subject_teacher_username = get_student_proposal_panel_invitation[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_panel_invitation[i].subject_teacher_full_name,

                is_completed = get_student_proposal_panel_invitation[i].is_completed,
            )
            log_proposal_panel_invitation.save()
            i + 1
        print("Proposal Panel Invitation - Log - Successfully")
        
        # Proposal Defense Schedule Logs
        for i in range (len(get_student_proposal_defense_schedule)):
            log_proposal_defense_schedule = DefenseScheduleLog(
                username = get_student_proposal_defense_schedule[i].username,
                name = get_student_proposal_defense_schedule[i].name,
                student_leader_username = get_student_proposal_defense_schedule[i].student_leader_username,
                student_leader_name = get_student_proposal_defense_schedule[i].student_leader_name,
                course = get_student_proposal_defense_schedule[i].course,
                form = get_student_proposal_defense_schedule[i].form,
                date = get_student_proposal_defense_schedule[i].date,
                start_time = get_student_proposal_defense_schedule[i].start_time,
                end_time = get_student_proposal_defense_schedule[i].end_time,
                status = "Re-Defense",
            )
            log_proposal_defense_schedule.save()
            i + 1
        print("Proposal Defense Schedule - Log - Successfully")

        for i in range (len(get_student_proposal_defense_forms)):
            log_proposal_defense_form = ProposalDefenseFormLog(
                student_leader_username = get_student_proposal_defense_forms[i].student_leader_username ,
                student_leader_full_name = get_student_proposal_defense_forms[i].student_leader_full_name ,
                course_major_abbr = get_student_proposal_defense_forms[i].course_major_abbr,

                panel_username = get_student_proposal_defense_forms[i].panel_username ,
                panel_full_name = get_student_proposal_defense_forms[i].panel_full_name ,
                panel_attendance = get_student_proposal_defense_forms[i].panel_attendance ,
                panel_signature_response = get_student_proposal_defense_forms[i].panel_signature_response ,
                panel_signature_attach = get_student_proposal_defense_forms[i].panel_signature_attach ,

                is_panel_chairman = get_student_proposal_defense_forms[i].is_panel_chairman ,
                panel_chairman_signature_response = get_student_proposal_defense_forms[i].panel_chairman_signature_response ,
                panel_chairman_signature_attach = get_student_proposal_defense_forms[i].panel_chairman_signature_attach ,

                form_date = get_student_proposal_defense_forms[i].form_date ,

                start_critique = get_student_proposal_defense_forms[i].start_critique ,
                end_critique = get_student_proposal_defense_forms[i].end_critique ,

                start_voting = get_student_proposal_defense_forms[i].start_voting ,
                end_voting = get_student_proposal_defense_forms[i].end_voting ,

                form_status = get_student_proposal_defense_forms[i].form_status ,
                form = get_student_proposal_defense_forms[i].form ,

                subject_teacher_username = get_student_proposal_defense_forms[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_defense_forms[i].subject_teacher_full_name,

                defense_date = get_student_proposal_defense_forms[i].defense_date,
                defense_start_time = get_student_proposal_defense_forms[i].defense_start_time,
                defense_end_time = get_student_proposal_defense_forms[i].defense_end_time,

                critique_sign_response = get_student_proposal_defense_forms[i].critique_sign_response ,
                proposal_defense_response = get_student_proposal_defense_forms[i].proposal_defense_response,
            )
            log_proposal_defense_form.save()
            i + 1
        print("Proposal Defense Forms - Log - Successfully")

        get_student_research_titles.delete()
        get_student_title_panel_invitation.delete()
        get_student_title_defense_schedule.delete()
        get_student_title_defense_form.delete()
        get_student_proposal_panel_invitation.delete()
        get_student_proposal_defense_schedule.delete()
        get_student_proposal_defense_forms.delete()
        
        StudentLeader.objects.filter(username=id).update(
            request_limit = 5, 

            research_titles_status = "",
            bet3_panel_invitation_status = "",
            title_defense_status = "",
            research_title_defense_date ="", 
            research_title_defense_start_time = "", 
            research_title_defense_end_time = "",

            bet3_proposal_defense_panel_invitation_status = "", 
            research_proposal_defense_date ="", 
            research_proposal_defense_start_time = "", 
            research_proposal_defense_end_time = ""
            )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet proposal defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)
        
# Subject Teacher - User Profile -  Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherProfile(request):
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

    return render(request, "subject-teacher-profile.html", context)


# Subject Teacher - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherUploadESignature(request):
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

                    return render(request, "subject-teacher-profile.html", context)
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

                    return render(request, "subject-teacher-profile.html", context)

                return redirect("subject-teacher-profile")

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

            return render(request, "subject-teacher-profile.html", context)


# Subject Teacher - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherCreateESignature(request):
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

        return redirect("subject-teacher-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "subject-teacher-signature-pad.html", context)


# Subject Teacher - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("subject-teacher-profile")


# Subject Teacher - Acount Settings Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherAccountSettings(request):
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

                    return render(request, "subject-teacher-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "subject-teacher-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "subject-teacher-account-settings.html", context)

    return render(request, "subject-teacher-account-settings.html", context)


##### SUBJECT TEACHER - BET-3 - TOPIC DEFENSE #####

# Subject Teacher - Research Title Defense Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherMyTitleDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, course=course_input, status="Reserved")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
            }

            return render(request, "subject-teacher-title-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-title-defense-schedule-dashboard.html", context)


# Subject Teacher - Research Title Defense Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherStudentsTitleDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, course=course_input, status="Reserved")
            student_defense_unscheduled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, research_title_defense_date="")

            print(student_defense_unscheduled)
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
                "student_defense_unscheduled": student_defense_unscheduled,
            }

            return render(request, "subject-teacher-students-title-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-students-title-defense-schedule-dashboard.html", context)


# Subject Teacher - Set Research Title Defense Schedule Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherSetResearchTitleDefenseSchedule(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        course_available_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username,form = "Research Title Defense", course=course_input, status="Available")
        course_reserved_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form = "Research Title Defense", course=course_input, status="Reserved")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "course_handled_list": course_handled_list, "course_available_defense_schedules": course_available_defense_schedules, "course_reserved_defense_schedules": course_reserved_defense_schedules}

        return render(request, "subject-teacher-set-research-title-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-title-defense.html", context)


# Subject Teacher - Save Research Title Defense Schedule Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherSaveResearchTitleDefenseSchedule(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []
    defense_time_list = ["8:00 AM-9:00 AM", "9:00 AM-10:00 AM", "10:00 AM-11:00 AM", "1:00 PM-2:00 PM", "2:00 PM-3:00 PM", "3:00 PM-4:00 PM", "4:00 PM-5:00 PM"]

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        date_input = request.POST.get("date_input")
        time_input = request.POST.get("time_input")

        if course_input not in course_handled_list:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "course_handled_list": course_handled_list, "response": "sweet invalid course"}

            return render(request, "subject-teacher-set-research-title-defense.html", context)

        if time_input not in defense_time_list:

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "course_handled_list": course_handled_list, "response": "sweet invalid defense time"}

            return render(request, "subject-teacher-set-research-title-defense.html", context)

        js_month = date_input.split("-")[1]
        js_date = date_input.split("-")[2]
        js_year = date_input.split("-")[0]

        start_time = time_input.split("-")[0]
        end_time = time_input.split("-")[1]

        py_date = date(day=int(js_date), month=int(js_month), year=int(js_year)).strftime("%B %d, %Y")

        print(course_input)
        print(py_date)
        print(start_time)
        print(end_time)

        try:
            DefenseSchedule.objects.get(username=currently_loggedin_user.username, form="Research Title Defense", date=py_date, start_time=start_time, end_time=end_time)

            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "course_handled_list": course_handled_list, "response": "scheduled date exist"}

            return render(request, "subject-teacher-set-research-title-defense.html", context)

        except:
            print("do not exist")
            pass

        defense_schedule = DefenseSchedule(username=currently_loggedin_user.username, name=currently_loggedin_user_full_name, course=course_input, form="Research Title Defense", date=py_date, start_time=start_time, end_time=end_time, status="Available")
        defense_schedule.save()

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "course_handled_list": course_handled_list, "response": "schedule saved"}

        return render(request, "subject-teacher-set-research-title-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-title-defense.html", context)


# Subject Teacher - Delete Research Title Defense Schedule Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherDeleteResearchTitleDefenseSchedule(request, id):
    currently_loggedin_user = request.user

    delete_date = DefenseSchedule.objects.filter(username=currently_loggedin_user.username, id=id, status="Available")
    print(delete_date)

    if not delete_date:
        context = {"response": "sweet schedule not found"}

        return render(request, "subject-teacher-set-research-title-defense.html", context)

    else:
        delete_date.delete()

        context = {"response": "schedule deleted"}

        return render(request, "subject-teacher-set-research-title-defense.html", context)


# Subject Teacher - BET-3 Research Title Defense Logs Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3TitleDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_completed_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, status="Completed")
    get_redefense_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, status="Re-Defense")
    get_reschedule_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, status="Reschedule")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "completed_defense_schedule": get_completed_defense_schedule,
        "redefense_defense_schedule": get_redefense_defense_schedule,
        "reschedule_defense_schedule": get_reschedule_defense_schedule,
    }

    return render(request, "subject-teacher-bet3-research-title-defense-logs.html", context)


# Subject Teacher - BET-3 Research Title Defense Completed Logs Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3TitleDefenseLogCompleted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("subject-teacher-bet3-title-defense-logs")

    get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = ResearchTitle.objects.all().filter(student_leader_username=id)

    get_present_panel_members = TitleDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")
    get_absent_panel_members = TitlePanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="absent")

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Revise Title")
    except:
        get_research_title_revise = None

    if get_student_leader_data.middle_name == " ":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "student_leader_data": get_student_leader_data, "student_leader_full_name": student_leader_full_name, "group_members": get_student_group_members, "research_titles": get_research_titles, "research_title_accepted": get_research_title_accepted, "research_title_revise": get_research_title_revise, "present_panel_members": get_present_panel_members, "absent_panel_members": get_absent_panel_members}

    return render(request, "subject-teacher-bet3-research-title-defense-data.html", context)


# Subject Teacher - BET-3 Research Title Defense Redefense Logs Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherBET3TitleDefenseLogRedefense(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = ResearchTitleLog.objects.all().filter(student_leader_username=id)

    get_present_panel_members = TitleDefenseFormLog.objects.all().filter(student_leader_username=id, panel_attendance="present")
    get_absent_panel_members = TitlePanelInvitationLog.objects.all().filter(student_leader_username=id, form_status="accepted", form="BET-3 Panel Invitation", panel_attendance="absent")

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Revise Title")
    except:
        get_research_title_revise = None

    defense_date = get_present_panel_members[0].defense_date
    defense_start_time = get_present_panel_members[0].defense_start_time
    defense_end_time = get_present_panel_members[0].defense_end_time

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_full_name": get_research_titles[0].student_leader_name,
        "student_course": get_research_titles[0].course_major_abbr,
        "group_members": get_student_group_members,
        "research_titles": get_research_titles,
        "research_title_accepted": get_research_title_accepted,
        "research_title_revise": get_research_title_revise,
        "defense_date": defense_date,
        "defense_start_time": defense_start_time,
        "defense_end_time": defense_end_time,
        "present_panel_members": get_present_panel_members,
        "absent_panel_members": get_absent_panel_members,
    }

    return render(request, "subject-teacher-bet3-research-title-defense-data.html", context)

##### SUBJECT TEACHER - BET-3 - PROPOSAL DEFENSE #####

# Subject Teacher - Research Proposal Defense Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherMyProposalDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Proposal Defense", course=course_input, status="Reserved")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
            }

            return render(request, "subject-teacher-proposal-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-proposal-defense-schedule-dashboard.html", context)


# Subject Teacher - Research Proposal Defense Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherStudentsProposalDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, course=course_input, form = "Research Proposal Defense", status="Reserved")
            student_defense_unscheduled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, research_proposal_defense_date="")

            print(student_defense_unscheduled)
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
                "student_defense_unscheduled": student_defense_unscheduled,
            }

            return render(request, "subject-teacher-students-proposal-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-students-proposal-defense-schedule-dashboard.html", context)


# Subject Teacher - Set Research Proposal Defense Schedule Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherSetResearchProposalDefenseSchedule(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        course_available_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form = "Research Proposal Defense", course=course_input, status="Available")
        course_reserved_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form = "Research Proposal Defense", course=course_input, status="Reserved")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "course_handled_list": course_handled_list, 
            "course_available_defense_schedules": course_available_defense_schedules, 
            "course_reserved_defense_schedules": course_reserved_defense_schedules,
            }

        return render(request, "subject-teacher-set-research-proposal-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-proposal-defense.html", context)


# Subject Teacher - BET-3 Research Proposal Defense Form - Save Schedule
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherSaveResearchProposalDefenseSchedule(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []
    defense_time_list = ["8:00 AM-9:00 AM", "9:00 AM-10:00 AM", "10:00 AM-11:00 AM", "1:00 PM-2:00 PM", "2:00 PM-3:00 PM", "3:00 PM-4:00 PM", "4:00 PM-5:00 PM"]

    course_handled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        date_input = request.POST.get("date_input")
        time_input = request.POST.get("time_input")

        if course_input not in course_handled_list:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "course_handled_list": course_handled_list, 
                "response": "sweet invalid course"}

            return render(request, "subject-teacher-set-research-proposal-defense.html", context)

        if time_input not in defense_time_list:

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "course_handled_list": course_handled_list, 
                "response": "sweet invalid defense time"}

            return render(request, "subject-teacher-set-research-proposal-defense.html", context)

        js_month = date_input.split("-")[1]
        js_date = date_input.split("-")[2]
        js_year = date_input.split("-")[0]

        start_time = time_input.split("-")[0]
        end_time = time_input.split("-")[1]

        py_date = date(day=int(js_date), month=int(js_month), year=int(js_year)).strftime("%B %d, %Y")

        print(course_input)
        print(py_date)
        print(start_time)
        print(end_time)

        try:
            DefenseSchedule.objects.get(username=currently_loggedin_user.username, date=py_date, start_time=start_time, end_time=end_time)

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list, 
                "response": "scheduled date exist"}

            return render(request, "subject-teacher-set-research-proposal-defense.html", context)

        except:
            print("do not exist")
            pass

        defense_schedule = DefenseSchedule(
            username=currently_loggedin_user.username, 
            name=currently_loggedin_user_full_name, 
            course=course_input, form="Research Proposal Defense", 
            date=py_date, 
            start_time=start_time, 
            end_time=end_time, 
            status="Available"
            )

        defense_schedule.save()

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "course_handled_list": course_handled_list, 
            "response": "schedule saved"}

        return render(request, "subject-teacher-set-research-proposal-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-proposal-defense.html", context)


# Subject Teacher - Delete Research Proposal Defense Schedule
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="index")
def subjectTeacherDeleteResearchProposalDefenseSchedule(request, id):
    currently_loggedin_user = request.user

    delete_date = DefenseSchedule.objects.filter(username=currently_loggedin_user.username, id=id, status="Available")
    print(delete_date)

    if not delete_date:
        context = {"response": "sweet schedule not found"}

        return render(request, "subject-teacher-set-research-proposal-defense.html", context)

    else:
        delete_date.delete()

        context = {"response": "schedule deleted"}

        return render(request, "subject-teacher-set-research-proposal-defense.html", context)


# Adviser - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": get_adviser_data,
        "date_today": today.strftime("%B %d, %Y"),
    }

    return render(request, "adviser-dashboard.html", context)


# Adviser - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserProfile(request):
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

    return render(request, "adviser-profile.html", context)


# Adviser - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserUploadESignature(request):
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

                    return render(request, "adviser-profile.html", context)
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

                    return render(request, "adviser-profile.html", context)

                return redirect("adviser-profile")

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

            return render(request, "adviser-profile.html", context)


# Adviser - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("adviser-profile")


# Adviser - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserCreateESignature(request):
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

        return redirect("adviser-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "adviser-signature-pad.html", context)


# Adviser - Acount Settings Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserAccountSettings(request):
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

                    return render(request, "adviser-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "adviser-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "adviser-account-settings.html", context)

    return render(request, "adviser-account-settings.html", context)


# Adviser - Advisee Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserAdviseeDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Get Adviser Conforme
    get_all_advisee_data = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, form_status="Accepted")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": get_adviser_data,
        "all_advisee_data": get_all_advisee_data,
    }

    return render(request, "adviser-advisee-dashboard.html", context)


# Adviser - BET-3 - Adviser Conforme Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserBET3AdviserConforme(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Get Adviser Conforme
    get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": get_adviser_data,
        "date_today": today.strftime("%B %d, %Y"),
        "adviser_conformes": get_adviser_conforme,
    }

    return render(request, "adviser-bet3-adviser-conforme.html", context)



# Adviser - BET-3 - Adviser Conforme - Accept with Signature Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserBET3AdviserConformeAcceptSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Get Adviser Conforme
    get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": get_adviser_data,
        "date_today": today.strftime("%B %d, %Y"),
        "adviser_conformes": get_adviser_conforme,
        "response": "sweet no esign"
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.adviser_response = "Accepted"
        check_adviser_conforme.adviser_response_date = date_today
        check_adviser_conforme.form_status = "Accepted"
        check_adviser_conforme.adviser_signature = True

        check_adviser_conforme.save()

        get_adviser_data.advisee_count = get_adviser_data.advisee_count + 1
        get_adviser_data.save()

        get_student_leader_data = StudentLeader.objects.get(username=check_adviser_conforme.student_leader_username)
        get_student_leader_data.adviser_conforme_status = "Completed"
        get_student_leader_data.adviser_name = check_adviser_conforme.adviser_name
        get_student_leader_data.adviser_username = check_adviser_conforme.adviser_username
        get_student_leader_data.save()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "accepted_student_member_name": check_adviser_conforme.student_leader_full_name,
            "accepted_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme accepted",
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("adviser-bet3-adviser-conforme")


# Adviser - BET-3 - Adviser Conforme - Decline with Signature Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def adviserBET3AdviserConformeDeclineSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

   # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Get Adviser Conforme
    get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_data": get_adviser_data,
        "date_today": today.strftime("%B %d, %Y"),
        "adviser_conformes": get_adviser_conforme,
        "response": "sweet no esign"
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.adviser_response = "Declined"
        check_adviser_conforme.adviser_response_date = date_today
        check_adviser_conforme.adviser_signature = True
        check_adviser_conforme.form_status = "Declined"

        check_adviser_conforme.save()

        check_updated_adviser_conforme = AdviserConforme.objects.get(id=id)

        log_adviser_conforme = AdviserConformeLog(
            student_leader_username=check_updated_adviser_conforme.student_leader_username,
            student_leader_full_name=check_updated_adviser_conforme.student_leader_full_name,
            course=check_updated_adviser_conforme.course,
            research_title=check_updated_adviser_conforme.research_title,
            form_date_submitted=check_updated_adviser_conforme.form_date_submitted,
            dit_head_username=check_updated_adviser_conforme.dit_head_username,
            dit_head_name=check_updated_adviser_conforme.dit_head_name,
            dit_head_response=check_updated_adviser_conforme.dit_head_response,
            dit_head_response_date=check_updated_adviser_conforme.dit_head_response_date,
            adviser_username=check_updated_adviser_conforme.adviser_username,
            adviser_name=check_updated_adviser_conforme.adviser_name,
            adviser_response=check_updated_adviser_conforme.adviser_response,
            adviser_response_date=check_updated_adviser_conforme.adviser_response_date,
            form_status=check_updated_adviser_conforme.form_status,
        )
        log_adviser_conforme.save()
        check_updated_adviser_conforme.delete()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "declined_student_member_name": check_adviser_conforme.student_leader_full_name,
            "declined_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme declined",
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("adviser-bet3-adviser-conforme")


# Adviser - BET-3 - Adviser Conforme - Accept Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_adviser, login_url="index")
def adviserBET3AdviserConformeAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.adviser_response = "Accepted"
        check_adviser_conforme.adviser_response_date = date_today
        check_adviser_conforme.form_status = "Accepted"

        check_adviser_conforme.save()

        get_adviser_data.advisee_count = get_adviser_data.advisee_count + 1
        get_adviser_data.save()

        get_student_leader_data = StudentLeader.objects.get(username=check_adviser_conforme.student_leader_username)
        get_student_leader_data.adviser_conforme_status = "Completed"
        get_student_leader_data.adviser_name = check_adviser_conforme.adviser_name
        get_student_leader_data.adviser_username = check_adviser_conforme.adviser_username
        get_student_leader_data.save()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "accepted_student_member_name": check_adviser_conforme.student_leader_full_name,
            "accepted_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme accepted",
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("adviser-bet3-adviser-conforme")


# Adviser - BET-3 - Adviser Conforme - Decline Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_department_head, login_url="index")
def adviserBET3AdviserConformeDecline(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Adviser - Get Adviser Data
    try:
        get_adviser_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("index")

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        check_adviser_conforme.adviser_response = "Declined"
        check_adviser_conforme.adviser_response_date = date_today
        check_adviser_conforme.form_status = "Declined"

        check_adviser_conforme.save()

        check_updated_adviser_conforme = AdviserConforme.objects.get(id=id)

        log_adviser_conforme = AdviserConformeLog(
            student_leader_username=check_updated_adviser_conforme.student_leader_username,
            student_leader_full_name=check_updated_adviser_conforme.student_leader_full_name,
            course=check_updated_adviser_conforme.course,
            research_title=check_updated_adviser_conforme.research_title,
            form_date_submitted=check_updated_adviser_conforme.form_date_submitted,
            dit_head_username=check_updated_adviser_conforme.dit_head_username,
            dit_head_name=check_updated_adviser_conforme.dit_head_name,
            dit_head_response=check_updated_adviser_conforme.dit_head_response,
            dit_head_response_date=check_updated_adviser_conforme.dit_head_response_date,
            adviser_username=check_updated_adviser_conforme.adviser_username,
            adviser_name=check_updated_adviser_conforme.adviser_name,
            adviser_response=check_updated_adviser_conforme.adviser_response,
            adviser_response_date=check_updated_adviser_conforme.adviser_response_date,
            form_status=check_updated_adviser_conforme.form_status,
        )
        log_adviser_conforme.save()
        check_updated_adviser_conforme.delete()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(adviser_username=currently_loggedin_user.username, adviser_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "adviser_conformes": get_adviser_conforme,
            "declined_student_member_name": check_adviser_conforme.student_leader_full_name,
            "declined_student_member_username": check_adviser_conforme.student_leader_username,
            "response": "sweet bet-3 adviser conforme declined",
        }

        return render(request, "adviser-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("adviser-bet3-adviser-conforme")


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
