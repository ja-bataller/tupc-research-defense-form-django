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

today = date.today()
date_today = today.strftime("%B %d, %Y")

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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.adviser_name + " has accepted your Adviser Conforme, and is now your Research Adviser. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day.",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.adviser_name + " has declined your Adviser Conforme, you can try applying to other Faculty. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day.",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.adviser_name + " has accepted your Adviser Conforme, and is now your Research Adviser. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day.",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.adviser_name + " has declined your Adviser Conforme, you can try applying to other Faculty. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day.",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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