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


today = date.today()
date_today = today.strftime("%B %d, %Y")


# Admin - Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminDashboard(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_all_faculty = User.objects.all().filter(is_superuser = False, is_student = False, is_administrator = False)
    count_all_faculty = get_all_faculty.count()

    get_all_students = StudentLeader.objects.all()
    get_all_group_members = StudentGroupMember.objects.all()
    count_all_students = get_all_students.count() + get_all_group_members.count()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "date_today": date_today,

        "count_all_faculty": count_all_faculty,
        "count_all_students": count_all_students,
        }

    return render(request, "admin-dashboard.html", context)


# Admin - Profile Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
                    return render(request, "login.html", context)

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


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminStudentAccount(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_all_student = StudentLeader.objects.all()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,

        "students": get_all_student,
    }

    return render(request, "admin-student-account.html", context)


# Admin - Faculty Member Individual Account Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminStudentLeaderData(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        member_check = User.objects.get(username=id)
        student_leader_check = StudentLeader.objects.get(username=id)
    except:
        return redirect("admin-students-account")

    get_all_student = StudentLeader.objects.all()


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
        "member_username": member_username,
        "member_email": member_email,
        "member_first_name": member_first_name,
        "member_middle_name": member_middle_name,
        "member_last_name": member_last_name,
        "member_suffix": member_suffix,
        "member_department": member_department,
        "students": get_all_student,
    }

    if request.method == "POST":
        suffix_list = ["", "Sr.", "Jr.", "I", "II", "III", "IV", "V"]

        username_input = request.POST.get("username_input")
        email_input = request.POST.get("email_input")
        first_name_input = request.POST.get("first_name_input")
        middle_name_input = request.POST.get("middle_name_input")
        last_name_input = request.POST.get("last_name_input")
        suffix_input = request.POST.get("suffix_input")

        if suffix_input not in suffix_list:
            print("Suffix not in list")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "member_username": member_username, 
                "member_email": member_email, 
                "member_first_name": member_first_name, 
                "member_middle_name": member_middle_name, 
                "member_last_name": member_last_name, 
                "member_department": member_department,
                "students": get_all_student, 
                "response": "sweet invalid suffix"
                }

            return render(request, "admin-student-leader-data.html", context)

        if "TUPC" in username_input:
            pass

        else:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "member_username": member_username, 
                "member_email": member_email, 
                "member_first_name": member_first_name, 
                "member_middle_name": member_middle_name, 
                "member_last_name": member_last_name, 
                "member_department": member_department, 
                "students": get_all_student,
                "response": "invalid username"
                }

            return render(request, "admin-student-leader-data.html", context)

        if "gsfe.tupcavite.edu.ph" in email_input:
            pass

        else:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "member_username": member_username, 
                "member_email": member_email, 
                "member_first_name": member_first_name, 
                "member_middle_name": member_middle_name, 
                "member_last_name": member_last_name, 
                "member_department": member_department,
                "students": get_all_student,
                 "response": "invalid email"}

            return render(request, "admin-student-leader-data.html", context)

        member_check.first_name = first_name_input.title()
        member_check.middle_name = middle_name_input.title()
        member_check.last_name = last_name_input.title()
        member_check.suffix = suffix_input
        member_check.save()

        student_leader_check.first_name = first_name_input.title()
        student_leader_check.middle_name = middle_name_input.title()
        student_leader_check.last_name = last_name_input.title()
        student_leader_check.suffix = suffix_input
        student_leader_check.save()

        if member_check.username == username_input and member_check.email == email_input:

            sweet_member_check = User.objects.get(username=id)

            sweet_member_username = sweet_member_check.username
            sweet_member_full_name = None

            if sweet_member_check.middle_name == "":
                sweet_member_full_name = sweet_member_check.first_name + " " + sweet_member_check.last_name

            else:
                sweet_member_full_name = sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "sweet_member_username": sweet_member_username, 
                "sweet_member_full_name": sweet_member_full_name, 
                "students": get_all_student,
                "response": "sweet profile updated"}

            return render(request, "admin-student-account.html", context)

        if member_check.username != username_input and member_check.email == email_input:
            try:
                User.objects.get(username=username_input)

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
                    "sweet_member_username": sweet_member_username, 
                    "sweet_member_full_name": sweet_member_full_name, 
                    "students": get_all_student,
                    "response": "sweet partial update username exist"
                    }

                return render(request, "admin-student-account.html", context)

            except:
                member_check.username = username_input
                member_check.save()

                student_leader_check.username = username_input
                student_leader_check.save()

                members = User.objects.all().filter(is_faculty_member=1)

                sweet_member_check = User.objects.get(username=username_input)

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
                    "students": get_all_student,
                    "response": "sweet profile updated"
                    }

                return render(request, "admin-student-account.html", context)

        if member_check.username == username_input and member_check.email != email_input:

            try:
                User.objects.get(email=email_input)

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
                    "sweet_member_username": sweet_member_username, 
                    "sweet_member_full_name": sweet_member_full_name, 
                    "students": get_all_student,
                    "response": "sweet partial update email exist"
                    }

                return render(request, "admin-student-account.html", context)

            except: 
                member_check.email = email_input
                member_check.save()

                student_leader_check.email = email_input
                student_leader_check.save()

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
                    "sweet_member_username": sweet_member_username, 
                    "sweet_member_full_name": sweet_member_full_name, 
                    "students": get_all_student,
                    "response": "sweet profile updated"
                    }

                return render(request, "admin-student-account.html", context)

        if member_check.username != username_input and member_check.email != email_input:

            try:
                User.objects.get(username=username_input)
                User.objects.get(email=email_input)

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
                    "sweet_member_username": sweet_member_username, 
                    "sweet_member_full_name": sweet_member_full_name,
                    "students": get_all_student,
                    "response": "sweet partial update username and email exist"}

                return render(request, "admin-student-account.html", context)

            except:
                member_check.username = username_input
                member_check.email = email_input
                member_check.save()

                student_leader_check.username = username_input
                student_leader_check.email = email_input
                student_leader_check.save()
                

                sweet_member_check = User.objects.get(username=username_input)

                sweet_member_username = sweet_member_check.username
                sweet_member_full_name = None

                if sweet_member_check.middle_name == "":
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.last_name

                else:
                    sweet_member_full_name = sweet_member_check.honorific + " " + sweet_member_check.first_name + " " + sweet_member_check.middle_name[0] + ". " + sweet_member_check.last_name

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account,
                    "sweet_member_username": sweet_member_username, 
                    "sweet_member_full_name": sweet_member_full_name, 
                    "students": get_all_student,
                    "response": "sweet profile updated"
                    }

                return render(request, "admin-student-account.html", context)


    return render(request, "admin-student-leader-data.html", context)


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminStudentGroupMemberAccount(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_all_student = StudentGroupMember.objects.all()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,

        "students": get_all_student,
    }

    return render(request, "admin-group-members-account.html", context)


# Admin - Faculty Member Individual Account Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminStudentGroupMemberData(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_all_student = StudentGroupMember.objects.all()

    try:
        member_check = StudentGroupMember.objects.get(student_member_username=id)
    except:
        return redirect("admin-student-group-members-account")

    member_username = member_check.student_member_username
    member_full_name = member_check.student_member_full_name

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "member_username": member_username,
        "member_full_name": member_full_name,
    }

    if request.method == "POST":

        username_input = request.POST.get("username_input")
        email_input = request.POST.get("email_input")
        full_name_input = request.POST.get("full_name_input")

        if "TUPC" in username_input:
            pass

        else:
            context = {
                 "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "member_username": member_username,
                "member_full_name": member_full_name,
                "students": get_all_student,
                "response": "invalid username"
                }

            return render(request, "admin-group-members-data.html", context)

        member_check.student_member_full_name = full_name_input.title()
        member_check.save()

        if member_check.student_member_username == username_input:

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "sweet_member_username": member_username, 
                "sweet_member_full_name": full_name_input,
                "students": get_all_student,
                "response": "sweet profile updated"}

            return render(request, "admin-group-members-account.html", context)

        if member_check.student_member_username != username_input:
            try:
                User.objects.get(username=username_input)

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "sweet_member_username": member_username, 
                    "sweet_member_full_name": member_full_name, 
                    "students": get_all_student,
                    "response": "sweet partial update username exist"}

                return render(request, "admin-group-members-account.html", context)
            except:
                pass

            try:
                StudentGroupMember.objects.get(student_member_username=username_input)

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "sweet_member_username": member_username, 
                    "sweet_member_full_name": member_full_name, 
                    "students": get_all_student,
                    "response": "sweet partial update username exist"}

                return render(request, "admin-group-members-account.html", context)

            except:
                member_check.student_member_username = username_input
                member_check.save()

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "sweet_member_username": username_input, 
                    "sweet_member_full_name": full_name_input,
                    "students": get_all_student,
                    "response": "sweet profile updated"
                     }

                return render(request, "admin-group-members-account.html", context)

    return render(request, "admin-group-member-data.html", context)


# Admin - Student Course and Major Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
        old_abbr = course_major_check.course_major_abbr
        print(old_abbr)

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

        StudentLeader.objects.filter(course_major_abbr = old_abbr).update(course =  course_major_check.course, major = course_major_check.major, course_major_abbr = course_major_check_new.course_major_abbr)
        StudentGroupMember.objects.filter(course_major_abbr = old_abbr).update(course =  course_major_check.course, major = course_major_check.major, course_major_abbr = course_major_check_new.course_major_abbr)

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminResearchTitles(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    user_middle_name = current_user.middle_name
    user_middle_initial = None

    get_research_titles = ResearchTitle.objects.all()
    get_research_title_logs = ResearchTitleLog.objects.all()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "research_titles": get_research_titles,
        "research_title_logs": get_research_title_logs,
    }

    return render(request, "admin-research-titles.html", context)


# Admin - Department Head Account Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminFacultyMemberData(request, id):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    print(id)

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

                    try:
                        AcknowledgementReceipt.objects.filter(dit_head_username = id).update(dit_head_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(adaa_username = id).update(adaa_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(library_username = id).update(library_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(research_ext_username = id).update(research_ext_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(adviser_username = id).update(adviser_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(subject_teacher_username = id).update(subject_teacher_username = username_input)
                    except:
                        pass

                    try:
                        AcknowledgementReceipt.objects.filter(adaa_username = id).update(adaa_username = username_input)
                    except:
                        pass
                    
                    try:
                        TitlePanelInvitation.objects.filter(panel_username = id).update(panel_username = username_input)
                    except:
                        pass
                        
                    try:
                        TitleDefenseForm.objects.filter(panel_username = id).update(panel_username = username_input)
                    except:
                        pass

                    try:
                        TitleVote.objects.filter(panel_username = id).update(panel_username = username_input)
                    except:
                        pass
                        
                    try:
                        AcknowledgementReceipt.objects.filter(panel_username = id).update(panel_username = username_input)
                    except:
                        pass

                    
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
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

                    try:
                        print("Exist")
                        check_dit_head = User.objects.get(is_department_head=1)
                        print("pass")

                        members = User.objects.all().filter(is_faculty_member=1)

                        sweet_member_check = User.objects.get(username=id)

                        sweet_member_username = sweet_member_check.username

                        context = {
                            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                            "currently_loggedin_user_account": currently_loggedin_user_account,
                            "members": members,
                            "sweet_member_username": sweet_member_username,
                            "response": "sweet dit head exist",
                        }

                        return render(request, "admin-faculty-member-account.html", context)
                    except:
                        pass

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


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminAdviseeLimit(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_current_advisee_limit = User.objects.filter(is_panel = 1)

    current_advisee_limit = get_current_advisee_limit[0].advisee_limit
    print(current_advisee_limit)

    advisee_limit_list = []

    for i in range(len(get_current_advisee_limit)):
        advisee_limit_list.append(get_current_advisee_limit[i].advisee_count)
        i + 1
    
    max_advisee_count = max(advisee_limit_list)
    print(max_advisee_count)


    if request.method == "POST":
        advisee_limit_input = request.POST.get("advisee_limit_input")
        print(advisee_limit_input)
        
        if int(advisee_limit_input) < 5:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "current_advisee_limit":current_advisee_limit,
                "response": "sweet advisee limit less minimum"
            }

            return render(request, "admin-advisee-limit.html", context)
        
        if int(max_advisee_count) > int(advisee_limit_input) or int(advisee_limit_input) == 0:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "current_advisee_limit":current_advisee_limit,
                "response": "sweet advisee limit invalid"
            }

            return render(request, "admin-advisee-limit.html", context)

        
        User.objects.filter(is_panel = 1).update(advisee_limit = advisee_limit_input)

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "currently_loggedin_user_account": currently_loggedin_user_account,
            "current_advisee_limit":current_advisee_limit,
            "response": "sweet advisee limit updated"
        }

        return render(request, "admin-advisee-limit.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "current_advisee_limit":current_advisee_limit,
    }

    return render(request, "admin-advisee-limit.html", context)


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminAdviseeLimitSet(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_current_advisee_limit = User.objects.get(is_panel = 1)

    current_advisee_limit = get_current_advisee_limit.advisee_limit
    print(current_advisee_limit)

    if request.method == "POST":
        advisee_limit_input = request.POST.get("advisee_limit_input")
        print(advisee_limit_input)

        if advisee_limit_input < 5:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "response": "sweet advisee limit less minimum"
            }

            return render(request, "admin-advisee-limit.html", context)



    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
    }

    return render(request, "admin-advisee-limit.html", context)


# Admin
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_administrator, login_url="login")
def adminTheDevs(request):
    current_user = request.user
    current_password = current_user.password

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    user_middle_name = current_user.middle_name
    user_middle_initial = None

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
    }

    return render(request, "admin-the-devs.html", context)


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