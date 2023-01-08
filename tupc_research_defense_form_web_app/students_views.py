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
from docx.enum.text import WD_ALIGN_PARAGRAPH
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


# Student - Add Research Title - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentResearchTitleUpdate(request):
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


    try:
        get_revise_research_title = ResearchTitle.objects.get(student_leader_username=current_user.username, title_defense_status = "Revise Title", old_research_title = "")

    except:
        return redirect("student-research-title-dashboard")

    
    if request.method == "POST":
        input_revise_research_title = request.POST.get("input_revise_research_title")
        ResearchTitle.objects.filter(student_leader_username=current_user.username, title_defense_status = "Revise Title", old_research_title = "").update(research_title = input_revise_research_title, old_research_title = get_revise_research_title.research_title)

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "revise_research_title": get_revise_research_title,
            "response": "sweet revise title success"
            }

        return render(request, "student-research-title-dashboard.html", context)

    
    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "revise_research_title": get_revise_research_title}

    return render(request, "student-research-title-update.html", context)
    
    
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

    defense_dates = DefenseSchedule.objects.all().filter(course=get_student_leader_data.course_major_abbr, username=get_student_leader_data.bet3_subject_teacher_username, status="Available", form = "Research Title Defense")

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

            # Send g-mail notifications
            send_mail(
                "Panel Invitation for Topic Defense",
                "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Topic Defense. \nThank you and Have a nice day.",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )

        except:
            # Check if the entered Defense Scheduled is valid
            if int(defense_schedule_input) not in defense_date_list:

                context = {
                    "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                    "currently_loggedin_user_account": currently_loggedin_user_account, 
                    "dept_head_name": dept_head_name, 
                    "panel_members": panel_members, 
                    "defense_dates": defense_dates,
                     "response": "sweet invalid defense schedule"}

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

                # Send g-mail notifications
                send_mail(
                    "Panel Invitation for Topic Defense",
                    "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Topic Defense. \nThank you and Have a nice day.",
                    "unofficial.tupc.uitc@gmail.com",
                    ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                    fail_silently=False,
                )

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

# Student - BET3 - Topic - Panel Conforme - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3TopicPanelConforme(request):
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

    get_all_topic_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Topic Panel Conforme")

    get_all_pending_topic_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Topic Panel Conforme", is_completed = False)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "topic_panel_conforme": get_all_topic_panel_conforme,
        "pending_panel_conforme": get_all_pending_topic_panel_conforme,
    }

    return render(request, "student-bet3-topic-panel-conforme-dashboard.html", context)

# Student - BET3 - Panel Conforme - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentTopicPanelConformeSave(request):
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

    get_student_leader_data.topic_panel_conforme = "completed"
    get_student_leader_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "response": "sweet panel conforme saved"}

    return render(request, "student-bet3-topic-panel-conforme-dashboard.html", context)


# Student - BET3 - Proposal - Panel Conforme - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ProposalPanelConforme(request):
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
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    get_all_proposal_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Proposal Panel Conforme")

    get_all_pending_proposal_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Proposal Panel Conforme", is_completed = False)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "proposal_panel_conforme": get_all_proposal_panel_conforme,
        "pending_panel_conforme": get_all_pending_proposal_panel_conforme,
    }

    return render(request, "student-bet3-proposal-panel-conforme-dashboard.html", context)


# Student - BET3 - Panel Conforme - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentProposalPanelConformeSave(request):
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

    get_student_leader_data.proposal_panel_conforme = "completed"
    get_student_leader_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "response": "sweet panel conforme saved"}

    return render(request, "student-bet3-proposal-panel-conforme-dashboard.html", context)



# Student - BET5 - Final - Panel Conforme - Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5FinalPanelConforme(request):
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

    if get_student_leader_data.adviser_conforme_status != "Completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

        return render(request, "student-bet3-adviser-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.bet5_subject_teacher_username == "":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet no bet5 subject teacher"}

        return render(request, "student-bet5-subject-teacher.html", context)
    
    if get_student_leader_data.bet5_final_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final panel invitation"}

        return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet5_final_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    get_all_proposal_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Final Panel Conforme")

    get_all_pending_proposal_panel_conforme = PanelConforme.objects.all().filter(student_leader_username=current_user.username, form = "Final Panel Conforme", is_completed = False)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "proposal_panel_conforme": get_all_proposal_panel_conforme,
        "pending_panel_conforme": get_all_pending_proposal_panel_conforme,
    }

    return render(request, "student-bet5-final-panel-conforme-dashboard.html", context)


# Student - BET5 - Final Panel Conforme - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentFinalPanelConformeSave(request):
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

    get_student_leader_data.final_panel_conforme = "completed"
    get_student_leader_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "response": "sweet panel conforme saved"}

    return render(request, "student-bet5-final-panel-conforme-dashboard.html", context)



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

        # Send g-mail notifications
        send_mail(
            "Adviser Conforme",
            "Good Day " + dit_head_name + ",\n" + student_leader_full_name +" ("+get_student_leader_data.course_major_abbr+")" + " needs an approval for Adviser Conforme.\nThank you and Have a nice day.",
            get_student_leader_data.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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

    if get_student_leader_data.bet3_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "response": "sweet incomplete bet3 panel invitation"}

        return render(request, "student-bet3-panel-invitation-dashboard.html", context)

    if get_student_leader_data.title_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete title defense"}

        return render(request, "student-dashboard.html", context)

    try:
        ResearchTitle.objects.get(student_leader_username=current_user.username, title_defense_status = "Revise Title", old_research_title = "")
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "response": "sweet unathorized update research titles"}

        return render(request, "student-research-title-update.html", context)
    except:
        pass
    
    # if get_student_leader_data.adviser_conforme_status != "Completed":
    #     context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

    #     return render(request, "student-bet3-adviser-dashboard.html", context)
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
        
        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Proposal Defense. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )
            
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

            # Send g-mail notifications
            send_mail(
                "Panel Invitation for Topic Defense",
                "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Proposal Defense. \nThank you and Have a nice day.",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )

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

                get_student_leader_data.research_proposal_defense_date = save_defense_schedule.date
                get_student_leader_data.research_proposal_defense_start_time = save_defense_schedule.start_time
                get_student_leader_data.research_proposal_defense_end_time = save_defense_schedule.end_time
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

                # Send g-mail notifications
                send_mail(
                    "Panel Invitation for Topic Defense",
                    "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Proposal Defense. \nThank you and Have a nice day.",
                    "unofficial.tupc.uitc@gmail.com",
                    ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                    fail_silently=False,
                )

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



# Student - BET3 - Critique Form - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3CritiqueForm(request):
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
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    # Get Student Group Members
    try:
        get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    except:
        get_student_group_members = None

    # Get Student Proposal Defense Accepted with Revision
    try:
        get_accepted_proposal_title = ResearchTitle.objects.get(student_leader_username=current_user.username, proposal_defense_status = "Accepted with Revision")
    except:
        print("pass research titles")
        return redirect("student-dashboard")

    if get_student_leader_data.group_members_status != "completed" and get_student_leader_data.research_titles_status != "completed" and get_student_leader_data.bet3_panel_invitation_status != "completed":
        return redirect("student-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    get_critique_form = ProposalDefenseCritique.objects.all().filter(student_leader_username=current_user.username)
    get_proposal_defense_form = ProposalDefenseForm.objects.all().filter(student_leader_username=current_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "student_group_members": get_student_group_members,
        "student_research_title": get_accepted_proposal_title,
        "critiques": get_critique_form,
        "proposal_defense_form": get_proposal_defense_form,
    }

    return render(request, "student-bet3-critique-form.html", context)



# Student - BET3 - Research Proposal Defense Form - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET3ResearchProposalDefenseForm(request):
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
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    # Get Student Group Members
    try:
        get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    except:
        get_student_group_members = None

    # Get Student Proposal Defense Accepted with Revision
    try:
        get_accepted_proposal_title = ResearchTitle.objects.get(student_leader_username=current_user.username, proposal_defense_status = "Accepted with Revision")
    except:
        print("pass research titles")
        return redirect("student-dashboard")

    if get_student_leader_data.group_members_status != "completed" and get_student_leader_data.research_titles_status != "completed" and get_student_leader_data.bet3_panel_invitation_status != "completed":
        return redirect("student-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    get_proposal_defense_form = ProposalDefenseForm.objects.all().filter(student_leader_username=current_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "student_group_members": get_student_group_members,
        "student_research_title": get_accepted_proposal_title,
        "proposal_defense_form": get_proposal_defense_form,
    }

    return render(request, "student-bet3-research-proposal-defense.html", context)



# Student - BET5 - Subject Teacher
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5SubjectTeacher(request):
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
    
    if get_student_leader_data.adviser_conforme_status != "Completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

        return render(request, "student-bet3-adviser-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete panel invitation proposal defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############



    if get_student_leader_data.bet5_subject_teacher_username:
        return redirect("student-dashboard")
    
    # Faculty - Get all Faculty Member
    try:
        get_all_faculty = User.objects.all().filter(is_faculty_member = True)
    except:
        return redirect("index")
    
    if request.method == "POST":
        input_bet5_subject_teacher = request.POST.get("input_bet5_subject_teacher")
        print("Input BET-5 Subject Teacher: ", input_bet5_subject_teacher)

        # Check if Subject Teacher is in the DB
        try:
            check_subject_teacher = User.objects.get(username = input_bet5_subject_teacher)
            if check_subject_teacher.middle_name == "":
                faculty_full_name = check_subject_teacher.honorific + " " + check_subject_teacher.first_name + " " + check_subject_teacher.last_name + " " + check_subject_teacher.suffix
            else:
                faculty_full_name = check_subject_teacher.honorific + " " + check_subject_teacher.first_name + " " + check_subject_teacher.middle_name[0] + ". " + check_subject_teacher.last_name + " " + check_subject_teacher.suffix

            StudentLeader.objects.filter(username=current_user.username).update(bet5_subject_teacher_username = check_subject_teacher.username, bet5_subject_teacher_name = faculty_full_name)
            
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "bet3_subject_teacher": get_student_leader_data.bet3_subject_teacher_name,
                "all_faculty": get_all_faculty,
                "response": "sweet bet5 subject teacher saved"
            }
            return render(request, "student-bet5-subject-teacher.html", context)

        except:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account,
                "bet3_subject_teacher": get_student_leader_data.bet3_subject_teacher_name,
                "all_faculty": get_all_faculty,
                "response": "sweet subject teacher not found"
            }

            return render(request, "student-bet5-subject-teacher.html", context)


        


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "bet3_subject_teacher": get_student_leader_data.bet3_subject_teacher_name,
        "all_faculty": get_all_faculty,
    }

    return render(request, "student-bet5-subject-teacher.html", context)


# Student - BET5 - Final Defense - Panel Invitation
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5FinalDefensePanelInvitation(request):
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

    if get_student_leader_data.adviser_conforme_status != "Completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

        return render(request, "student-bet3-adviser-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.bet5_subject_teacher_username == "":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet no bet5 subject teacher"}

        return render(request, "student-bet5-subject-teacher.html", context)
    
    ############## PAGE VALIDATION ##############

    get_topic_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)

    get_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
    get_accepted_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
    get_pending_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")


    get_topic_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
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

    return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)


# Student - BET5 - Final Defense - Panel Invitation - Create for previous Panel Members
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5FinalDefensePanelInvitationCreatePanel(request):
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

    if get_student_leader_data.bet5_final_defense_panel_invitation_status == "completed":
        return redirect("student-bet5-final-defense-panel-invitation")
    ############## PAGE VALIDATION ##############

    # Topic Defense - Panel Invitation - Get Previous Panel Members
    get_previous_panel_members = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, panel_attendance = "present")
    previous_panel_member_count = get_previous_panel_members.count()

    # Proposal  Defense - Panel Invitation - Get Pending Panel Members
    get_proposal_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status = "pending")
    proposal_defense_count = get_proposal_panel_invitations.count()

    # Users - Get all Panel Members
    panel_members = User.objects.all().filter(is_panel=1)

    # Defense Schedule - Get all Proposal Defense Schedule
    defense_dates = DefenseSchedule.objects.all().filter(course=get_student_leader_data.course_major_abbr, username=get_student_leader_data.bet5_subject_teacher_username, form="Research Final Defense", status="Available")

    # If Student has no Research Proposal Defense Schedule
    if get_student_leader_data.research_final_defense_date != "":
        pass
    else:
        if not defense_dates:
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "response": "sweet no defense schedule"}

            return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
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

        return render(request, "student-bet5-final-defense-panel-invitation-create-panel.html", context)


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

        get_topic_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)

        get_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        get_accepted_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        get_pending_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")


        get_topic_panel_invitations = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
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

        return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)

    if request.method == "POST":
        defense_schedule_input = request.POST.get("defense_schedule_input")

        # Topic Defense - Panel Invitation - Get Previous Panel Members
        get_previous_panel_members = ProposalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, panel_attendance = "present")
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
            return render(request, "student-bet5-final-defense-panel-invitation-create-panel.html", context)

        else:

            # Defense Schedule - Save Proposal Defense Schedule
            try:
                save_defense_schedule = DefenseSchedule.objects.get(id=int(defense_schedule_input))

                save_defense_schedule.student_leader_username = current_user.username
                save_defense_schedule.student_leader_name = student_leader_full_name
                save_defense_schedule.status = "Reserved"
                save_defense_schedule.save()

                print("Student - Defense Schedule - Final Defense Schedule - Reserved")

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
            get_student_leader_data.research_final_defense_date = save_defense_schedule.date
            get_student_leader_data.research_final_defense_start_time = save_defense_schedule.start_time
            get_student_leader_data.research_final_defense_end_time = save_defense_schedule.end_time
            get_student_leader_data.request_limit = 5
            get_student_leader_data.save()
            print("Student - Student Leader -  Proposal Defense Schedule - Updated")

            for i in range(len(get_previous_panel_members)):
                send_proposal_defense_panel_invitation = FinalPanelInvitation(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name,
                    course_major_abbr=get_student_leader_data.course_major_abbr,

                    dit_head_username=dept_head.username,
                    dit_head_full_name=dept_head_name,
                    dit_head_response="pending",

                    panel_username=get_previous_panel_members[i].panel_username,
                    panel_full_name=get_previous_panel_members[i].panel_full_name,
                    panel_response="on hold",

                    research_final_defense_date=save_defense_schedule.date,
                    research_final_defense_start_time=save_defense_schedule.start_time,
                    research_final_defense_end_time=save_defense_schedule.end_time,

                    form_status="pending",
                    form_date_sent=today.strftime("%B %d, %Y"),
                    form="Final Defense Panel Invitation",

                    subject_teacher_username=get_student_leader_data.bet3_subject_teacher_username,
                    subject_teacher_full_name=get_student_leader_data.bet3_subject_teacher_name,
                    
                )
                send_proposal_defense_panel_invitation.save()
                i + 1
            
            # Send g-mail notifications
            send_mail(
                "Panel Invitation for Final Defense",
                "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Final Defense. \nThank you and Have a nice day.",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )
            

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account,

            "student_leader_data": get_student_leader_data,

            "dept_head_name": dept_head_name, 
            "panel_members": panel_members, 
            "defense_dates": defense_dates,

            "previous_panel": get_previous_panel_members,

            "response": "sweet panel invitation sent"}

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Final Defense. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )
            
        print("Student -  Proposal Defense Panel Invitation - Previous Panel Members - Sent")
        return render(request, "student-bet5-final-defense-panel-invitation-create-panel.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "dept_head_name": dept_head_name,
        "panel_members": panel_members,
        "defense_dates": defense_dates,

        "previous_panel": get_previous_panel_members,
    }

    return render(request, "student-bet5-final-defense-panel-invitation-create-panel.html", context)


# Student - BET5 - Final Defense - Panel Invitation - Create Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5FinalDefensePanelInvitationCreate(request):
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

    if get_student_leader_data.bet5_final_defense_panel_invitation_status == "completed":
        return redirect("student-bet5-final-defense-panel-invitation")
    ############## PAGE VALIDATION ##############

    try:
        get_pending_panel_invitation = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")
        pending_count = get_pending_panel_invitation.count()

        get_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
        get_accepted_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        get_pending_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

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

            return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
    except:
        pass

    
    try:
        get_accepted_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="accepted")
        accepted_count = get_accepted_panel_invitations.count()

        get_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username)
       
        get_pending_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=current_user.username, form_status="pending")

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

            return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
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

            return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
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

        return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)

    # Check if there is a Panel assigned.
    if not panel_members or panel_members.count() < 5:
        print("Incomplete Faculty Member")

        context = {"response": "sweet inc panel"}
        return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)
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

            return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)

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

            return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)

        # Check if the entered Panel Member is Subject Teacher
        try:
            StudentLeader.objects.get(username=current_user.username, bet5_subject_teacher_username=panel_input)

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "panel_full_name": panel_full_name, 
                "response": "sweet subject teacher"}

            return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Pending Panel Invitation
        try:
            FinalPanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="pending")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "currently_loggedin_user_account": currently_loggedin_user_account, 
                "student_leader_data": get_student_leader_data, 
                "dept_head_name": dept_head_name, 
                "panel_members": panel_members, 
                "defense_dates": defense_dates, 
                "panel_full_name": panel_full_name, 
                "response": "sweet panel invitation exist"}

            return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)
        except:
            pass

        # Check if the entered Panel Member has Accepted Panel Invitation
        try:
            FinalPanelInvitation.objects.get(student_leader_username=current_user.username, panel_username=panel_input, form_status="accepted")

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

            return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)
        except:
            pass

        try:
            check_defense_schedule = DefenseSchedule.objects.get(student_leader_username=current_user.username, form="Research Final Defense")
            print(check_defense_schedule)
            send_panel_invitation = FinalPanelInvitation(
                student_leader_username=current_user.username,
                student_leader_full_name=student_leader_full_name,
                course_major_abbr=get_student_leader_data.course_major_abbr,
                dit_head_username=dept_head.username,
                dit_head_full_name=dept_head_name,
                dit_head_response="pending",
                panel_username=get_panel_data.username,
                panel_full_name=panel_full_name,
                panel_response="on hold",
                research_final_defense_date=check_defense_schedule.date,
                research_final_defense_start_time=check_defense_schedule.start_time,
                research_final_defense_end_time=check_defense_schedule.end_time,
                form_status="pending",
                form_date_sent=date_today,
                form="Final Defense Panel Invitation",
                subject_teacher_username=get_student_leader_data.bet5_subject_teacher_username,
                subject_teacher_full_name=get_student_leader_data.bet5_subject_teacher_name,
            )
            send_panel_invitation.save()
            print("Panel Invitation Sent")

            # Send g-mail notifications
            send_mail(
                "Panel Invitation for Topic Defense",
                "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Final Defense. \nThank you and Have a nice day.",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )

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

                return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)
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

                    return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)

                get_student_leader_data.research_final_defense_date = save_defense_schedule.date
                get_student_leader_data.research_final_defense_start_time = save_defense_schedule.start_time
                get_student_leader_data.research_final_defense_end_time = save_defense_schedule.end_time
                get_student_leader_data.save()
                print("Student Leader Data Updated")

                send_panel_invitation = FinalPanelInvitation(
                    student_leader_username=current_user.username,
                    student_leader_full_name=student_leader_full_name,
                    course_major_abbr=get_student_leader_data.course_major_abbr,
                    dit_head_username=dept_head.username,
                    dit_head_full_name=dept_head_name,
                    dit_head_response="pending",
                    panel_username=get_panel_data.username,
                    panel_full_name=panel_full_name,
                    panel_response="on hold",
                    research_final_defense_date=save_defense_schedule.date,
                    research_final_defense_start_time=save_defense_schedule.start_time,
                    research_final_defense_end_time=save_defense_schedule.end_time,
                    form_status="pending",
                    form_date_sent=today.strftime("%B %d, %Y"),
                    form="Final Defense Panel Invitation",
                    subject_teacher_username=get_student_leader_data.bet5_subject_teacher_username,
                    subject_teacher_full_name=get_student_leader_data.bet5_subject_teacher_name,
                )
                send_panel_invitation.save()
                print("Panel Invitation Sent")

                # Send g-mail notifications
                send_mail(
                    "Panel Invitation for Topic Defense",
                    "Good Day " + dept_head_name + ",\n" + student_leader_full_name + " needs an approval for their Panel Invitation for Final Defense. \nThank you and Have a nice day.",
                    "unofficial.tupc.uitc@gmail.com",
                    ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                    fail_silently=False,
                )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "currently_loggedin_user_account": currently_loggedin_user_account, 
            "student_leader_data": get_student_leader_data, 
            "dept_head_name": dept_head_name, 
            "panel_members": panel_members, 
            "defense_dates": defense_dates, 
            "response": "sweet panel invitation sent"}

        return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "dept_head_name": dept_head_name,
        "panel_members": panel_members,
        "defense_dates": defense_dates,
    }

    return render(request, "student-bet5-final-defense-panel-invitation-create.html", context)


# Student - BET5 - Final Defense - Panel Invitation - Save Process
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5FinalDefensePanelInvitationSave(request):
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

    get_student_leader_data.bet5_final_defense_panel_invitation_status = "completed"
    get_student_leader_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "response": "sweet bet-3 panel invitation saved"}

    return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)



# Student - BET3 - Research Final Defense Form - Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentBET5ResearchFinalDefenseForm(request):
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

    if get_student_leader_data.adviser_conforme_status != "Completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

        return render(request, "student-bet3-adviser-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.bet5_subject_teacher_username == "":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet no bet5 subject teacher"}

        return render(request, "student-bet5-subject-teacher.html", context)
    
    if get_student_leader_data.bet5_final_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final panel invitation"}

        return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet5_final_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final defense"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    # Get Student Group Members
    try:
        get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=current_user.username)
    except:
        get_student_group_members = None

    # Get Student Proposal Defense Accepted with Revision
    try:
        get_accepted_proposal_title = ResearchTitle.objects.get(student_leader_username=current_user.username, final_defense_status = "Accepted with Revision")
    except:
        print("pass research titles")
        return redirect("student-dashboard")

    if get_student_leader_data.group_members_status != "completed" and get_student_leader_data.research_titles_status != "completed" and get_student_leader_data.bet5_final_defense_panel_invitation_status != "completed":
        return redirect("student-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    get_proposal_defense_form = FinalDefenseForm.objects.all().filter(student_leader_username=current_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "student_group_members": get_student_group_members,
        "student_research_title": get_accepted_proposal_title,
        "proposal_defense_form": get_proposal_defense_form,
    }

    return render(request, "student-research-final-defense.html", context)



# Student - Acknowledgement Receipt Dashboard
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentAcknowledgementReceiptDashboard(request):
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

    if get_student_leader_data.adviser_conforme_status != "Completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete adviser conforme"}

        return render(request, "student-bet3-adviser-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel invitation"}

        return render(request, "student-bet3-proposal-defense-panel-invitation-dashboard.html", context)
    
    if get_student_leader_data.bet3_proposal_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.bet5_subject_teacher_username == "":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet no bet5 subject teacher"}

        return render(request, "student-bet5-subject-teacher.html", context)
    
    if get_student_leader_data.bet5_final_defense_panel_invitation_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final panel invitation"}

        return render(request, "student-bet5-final-defense-panel-invitation-dashboard.html", context)

    if get_student_leader_data.bet5_final_defense_status != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final defense"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.topic_panel_conforme != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete topic panel conforme"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.proposal_panel_conforme != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete proposal panel conforme"}

        return render(request, "student-dashboard.html", context)
    
    if get_student_leader_data.final_panel_conforme != "completed":
        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account, "student_leader_data": get_student_leader_data, "date_today": date_today, "response": "sweet incomplete final panel conforme"}

        return render(request, "student-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    try:
        get_acknowledgement_receipt = AcknowledgementReceipt.objects.get(student_leader_username=current_user.username)
    except:
        get_acknowledgement_receipt = None

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "currently_loggedin_user_account": currently_loggedin_user_account,
        "student_leader_data": get_student_leader_data,
        "acknowledgement_receipt": get_acknowledgement_receipt,
    }

    return render(request, "student-acknowledgement-receipt-dashboard.html", context)


@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentAcknowledgementReceiptSave(request):
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

        return render(request, "student-acknowledgement-receipt-dashboard.html", context)
    ############## PAGE VALIDATION ##############

    get_student_leader_data.acknowledgement_receipt = "completed"
    get_student_leader_data.save()

    try:
        get_acknowledgement_receipt = AcknowledgementReceipt.objects.get(student_leader_username=current_user.username)
    except:
        pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "currently_loggedin_user_account": currently_loggedin_user_account, 
        "student_leader_data": get_student_leader_data, 
        "acknowledgement_receipt": get_acknowledgement_receipt,
        "response": "sweet acknowledgement receipt completed"}

    return render(request, "student-acknowledgement-receipt-dashboard.html", context)


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


# Student
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_student, login_url="index")
def studentTheDevs(request):
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

    return render(request, "student-the-devs.html", context)


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