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

# Set Timezone to Manila
# os.environ["TZ"] = "Asia/Manila"
# time.tzset()

today = date.today()
date_today = today.strftime("%B %d, %Y")

# Academic Affairs Office
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_receipt = AcknowledgementReceipt.objects.all().filter(adaa_response ="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "pending_receipt": get_pending_receipt,
    }

    return render(request, "adaa-dashboard.html", context)


# Research & Extension
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_accepted_receipt = AcknowledgementReceipt.objects.all().filter(adaa_response ="Accepted")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "accepted_receipt": get_accepted_receipt,
    }

    return render(request, "adaa-logs.html", context)


@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeTheDevs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
    }

    return render(request, "adaa-the-devs.html", context)

# Research & Extension - Profile Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeProfile(request):
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

    return render(request, "adaa-profile.html", context)


# Panel - Upload E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeUploadESignature(request):
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

                    return render(request, "adaa-profile.html", context)
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

                    return render(request, "adaa-profile.html", context)

                return redirect("academic-affairs-office-profile")

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

            return render(request, "adaa-profile.html", context)


# Panel - Remove E-Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("academic-affairs-office-profile")


# Panel - Dashboard Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeCreateESignature(request):
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

        return redirect("academic-affairs-office-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "adaa-signature-pad.html", context)


# Panel - Acount Settings Page
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeAccountSettings(request):
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

                    return render(request, "adaa-account-settings.html", context)

            else:
                context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password and new password is same"}

                return render(request, "adaa-account-settings.html", context)

        else:
            context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "response": "current password is incorrect"}

            return render(request, "adaa-account-settings.html", context)

    return render(request, "adaa-account-settings.html", context)


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    if currently_loggedin_user.middle_name == "":
        currently_loggedin_user_full_name = currently_loggedin_user.honorific + " " + currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user.middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.honorific + " " + currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass
        print("Panel - E-sign exist")

    else:
        print("Panel - E-sign doesn't exist.")
        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(adaa_response ="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": date_today,
            "pending_receipt": get_pending_receipt,
             "response": "sweet no esign",
        }
        return render(request, "adaa-dashboard.html", context)


    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.adaa_username = currently_loggedin_user.username
        check_receipt.adaa_full_name = currently_loggedin_user_full_name
        check_receipt.adaa_response = "Accepted"
        check_receipt.adaa_response_date = date_today
        check_receipt.adaa_signature = True

        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Academic Affairs Office) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(adaa_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel conforme accepted",
            }

        return render(request, "adaa-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("academic-affairs-office-dashboard")


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="index")
@user_passes_test(lambda u: u.is_academic_affairs, login_url="index")
def  academicAffairsOfficeAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    if currently_loggedin_user.middle_name == "":
        currently_loggedin_user_full_name = currently_loggedin_user.honorific + " " + currently_loggedin_user.first_name + " " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    else:
        currently_loggedin_user_middle_initial = currently_loggedin_user.middle_name[0]
        currently_loggedin_user_full_name = currently_loggedin_user.honorific + " " + currently_loggedin_user.first_name + " " + currently_loggedin_user_middle_initial + ". " + currently_loggedin_user.last_name + " " + currently_loggedin_user.suffix

    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.adaa_username = currently_loggedin_user.username
        check_receipt.adaa_full_name = currently_loggedin_user_full_name
        check_receipt.adaa_response = "Accepted"
        check_receipt.adaa_response_date = date_today

        check_receipt.save()

        print("pass -save")

        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Academic Affairs Office) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day.",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(adaa_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel conforme accepted",
            }

        return render(request, "adaa-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("adaa-dashboard")


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

    elif currently_loggedin_user.is_academic_affairs == 1:
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