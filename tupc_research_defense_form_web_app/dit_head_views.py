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
import datetime

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

today = date.today()
date_today = today.strftime("%B %d, %Y")

def adviserConformePendingRequests():
    date_today_int = today.strftime("%m/%d/%Y")
    print(date_today_int)
    pending_adviser_request = AdviserConforme.objects.all().filter(adviser_response = "Pending", adviser_response_date_exp = date_today_int)

    print(pending_adviser_request)
    if not pending_adviser_request:
        print("No Pending Adviser Conforme")
    else:
        pending_adviser_request.delete()
        print("Pending Adviser Conforme Deleted")
        

# DIT Head - Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadDashboard(request):
    adviserConformePendingRequests()
    
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_topic_panel_invitation = TitlePanelInvitation.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")
    get_pending_proposal_panel_invitation = ProposalPanelInvitation.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")
    get_pending_final_panel_invitation = FinalPanelInvitation.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")
    get_pending_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")
    get_pending_panel_conforme = PanelConforme.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")
    get_pending_acknowledgement_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response = "pending")

    context = {
        "currently_loggedin_user_data": currently_loggedin_user, 
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "date_today": date_today,

        "pending_topic_panel_invitation": get_pending_topic_panel_invitation.count(),
        "pending_proposal_panel_invitation": get_pending_proposal_panel_invitation.count(),
        "pending_final_panel_invitation": get_pending_final_panel_invitation.count(),
        "pending_adviser_conforme": get_pending_adviser_conforme.count(),
        "pending_panel_conforme": get_pending_panel_conforme.count(),
        "pending_acknowledgement_receipt":get_pending_acknowledgement_receipt.count()
        }

    return render(request, "dit-head-dashboard.html", context)


# DIT Head - Profile Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("dit-head-profile")


# DIT Head - Acount Settings - Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
                    return render(request, "login.html", context)

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


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadResearchTitles(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_research_titles = ResearchTitle.objects.all()
    get_research_title_logs = ResearchTitleLog.objects.all()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "research_titles": get_research_titles,
        "research_title_logs": get_research_title_logs,
    }

    return render(request, "dit-head-research-titles.html", context)


# DIT Head - BET3 - Topic - Panel Invitation
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Topic Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Topic Defense on " + check_panel_invitation.research_title_defense_date + " " + check_panel_invitation.research_title_defense_start_time + " to " + check_panel_invitation.research_title_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Topic Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Topic Defense on " + check_panel_invitation.research_title_defense_date + " " + check_panel_invitation.research_title_defense_start_time + " to " + check_panel_invitation.research_title_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " (DIT Head) has declined your Panel Invitation for Topic Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "panel_invitations": panel_invitation_bet3_check, "declined_student_member_name": check_panel_invitation.student_leader_full_name, "declined_student_member_username": check_panel_invitation.student_leader_username, "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - Panel Invitation BET-3 Decline Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " (DIT Head) has declined your Panel Invitation for Topic Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "panel_invitations": panel_invitation_bet3_check, "declined_student_member_name": check_panel_invitation.student_leader_full_name, "declined_student_member_username": check_panel_invitation.student_leader_username, "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-panel-invitation-bet-3.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-invitation-bet-3")


# DIT Head - BET3 - Proposal Defense - Panel Invitation - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Proposal Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Proposal Defense on " + check_panel_invitation.research_proposal_defense_date + " " + check_panel_invitation.research_proposal_defense_start_time + " to " + check_panel_invitation.research_proposal_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Proposal Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Proposal Defense on " + check_panel_invitation.research_proposal_defense_date + " " + check_panel_invitation.research_proposal_defense_start_time + " to " + check_panel_invitation.research_proposal_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has declined your Panel Invitation for Proposal Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has declined your Panel Invitation for Proposal Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        future_date = today + datetime.timedelta(days=7)
        future_date_formatted = future_date.strftime("%m/%d/%Y")

        print("Adviser Conforme Expire Date:",future_date_formatted)

        check_adviser_conforme.dit_head_response = "Accepted"
        check_adviser_conforme.dit_head_response_date = date_today
        check_adviser_conforme.adviser_response_date_exp = future_date_formatted
        check_adviser_conforme.dit_head_signature = True

        check_adviser_conforme.adviser_response = "Pending"
        check_adviser_conforme.save()

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.dit_head_name + " has accepted your Adviser Conforme request. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        send_mail(
            "Adviser Conforme",
            "Good Day " + check_adviser_conforme.adviser_name + ",\n" + check_adviser_conforme.student_leader_full_name +" ("+check_adviser_conforme.course+")" + " has requested you to be their Adviser for their Research. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )


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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET3AdviserConformeAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 - Check Adviser Conforme
    try:
        check_adviser_conforme = AdviserConforme.objects.get(id=id)

        future_date = today + datetime.timedelta(days=7)
        future_date_formatted = future_date.strftime("%m/%d/%Y")

        check_adviser_conforme.dit_head_response = "Accepted"
        check_adviser_conforme.dit_head_response_date = date_today
        check_adviser_conforme.adviser_response_date_exp = future_date_formatted
        check_adviser_conforme.adviser_response = "Pending"
        check_adviser_conforme.save()

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.dit_head_name + " has accepted your Adviser Conforme request. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        send_mail(
            "Adviser Conforme",
            "Good Day " + check_adviser_conforme.adviser_name + ",\n" + check_adviser_conforme.student_leader_full_name +" ("+check_adviser_conforme.course+")" + " has requested you to be their Adviser for their Research. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.dit_head_name + " has declined your Adviser Conforme request. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "adviser_conformes": get_adviser_conforme, "declined_student_member_name": check_adviser_conforme.student_leader_full_name, "declined_student_member_username": check_adviser_conforme.student_leader_username, "response": "sweet bet-3 adviser conforme declined"}

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT Head - BET-3 Adviser Conforme - Decline Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_adviser_conforme.student_leader_full_name + ",\n" + check_adviser_conforme.dit_head_name + " has declined your Adviser Conforme request. \nYou may click this link and login to your account. linkhere. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            currently_loggedin_user.email,
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # BET-3 - Get Adviser Conforme
        get_adviser_conforme = AdviserConforme.objects.all().filter(dit_head_response="Pending")

        context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "adviser_conformes": get_adviser_conforme, "declined_student_member_name": check_adviser_conforme.student_leader_full_name, "declined_student_member_username": check_adviser_conforme.student_leader_username, "response": "sweet bet-3 adviser conforme declined"}

        return render(request, "dit-head-bet3-adviser-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet3-adviser-conforme")


# DIT HEAD - ADVISER CONFORME

# DIT Head - BET3 - Panel Conforme - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadPanelConformeDashboard(request):
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

    get_panel_conforme = PanelConforme.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "get_panel_conforme": get_panel_conforme,
        "esignature_exist": esignature_exist,
    }

    return render(request, "dit-head-panel-conforme.html", context)


# DIT Head - Panel Conforme - Accept Signature Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadPanelConformeAcceptSignature(request, id):
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

        get_panel_conforme = PanelConforme.objects.all().filter(dit_head_username = currently_loggedin_user ,dit_head_response="Pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "get_panel_conforme": get_panel_conforme,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-panel-conforme.html", context)

    try:
        check_panel_conforme = PanelConforme.objects.get(id=id)

        check_panel_conforme.dit_head_response = "Accepted"
        check_panel_conforme.dit_head_response_date = date_today
        check_panel_conforme.dit_head_signature = True

        check_panel_conforme.panel_response = "Pending"
        check_panel_conforme.save()

        get_panel_conforme = PanelConforme.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response="Pending")

        # Email Notification - DIT Head to Student
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.student_leader_full_name + ",\n" + check_panel_conforme.dit_head_full_name + " has accepted your Panel Conforme for Topic Defense request.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # Email Notification - DIT Head to Panel
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.panel_full_name + ",\n" + check_panel_conforme.student_leader_full_name +" ("+check_panel_conforme.course_major_abbr+")" + " needs an approval for their Panel Conforme for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "get_panel_conforme": get_panel_conforme,
            "accepted_student_member_name": check_panel_conforme.student_leader_full_name,
            "accepted_student_member_username": check_panel_conforme.student_leader_username,
            "response": "sweet panel conforme accepted",
        }

        return render(request, "dit-head-panel-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-conforme")


# DIT Head - Panel Conforme - Accept Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadPanelConformeAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        check_panel_conforme = PanelConforme.objects.get(id=id)

        check_panel_conforme.dit_head_response = "Accepted"
        check_panel_conforme.dit_head_response_date = date_today

        check_panel_conforme.panel_response = "pending"

        check_panel_conforme.save()

        # Email Notification - DIT Head to Student
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.student_leader_full_name + ",\n" + check_panel_conforme.dit_head_full_name + " has accepted your Panel Conforme for Topic Defense request.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # Email Notification - DIT Head to Panel
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.panel_full_name + ",\n" + check_panel_conforme.student_leader_full_name +" ("+check_panel_conforme.course_major_abbr+")" + " needs an approval for their Panel Conforme for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        get_panel_conforme = PanelConforme.objects.all().filter(dit_head_username = currently_loggedin_user, dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "get_panel_conforme": get_panel_conforme,
            "accepted_student_member_name": check_panel_conforme.student_leader_full_name,
            "accepted_student_member_username": check_panel_conforme.student_leader_username,
            "response": "sweet panel conforme accepted",
        }

        return render(request, "dit-head-panel-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-panel-conforme")


# DIT Head - BET5 - Final Defense - Panel Invitation - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalDefensePanelInvitationDashboard(request):
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
    get_panel_invitation = FinalPanelInvitation.objects.all().filter(dit_head_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "esignature_exist": esignature_exist,
    }

    return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)


# DIT Head - BET5 - Final - Panel Invitation - Accept w/ Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalPanelInvitationAcceptSignature(request, id):
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
        get_panel_invitations = FinalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "pending"
        check_panel_invitation.save()

        get_panel_invitations = FinalPanelInvitation.objects.all().filter(dit_head_response="pending")

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Final Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Final Defense on " + check_panel_invitation.research_final_defense_date + " " + check_panel_invitation.research_final_defense_start_time + " to " + check_panel_invitation.research_final_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("DIT Head - Topic Panel Invitation doesn't exist.")
        return redirect("dit-head-bet5-final-defense-panel-invitation-dashboard")


# DIT Head - BET3 - Proposal - Panel Invitation - Accept Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalPanelInvitationAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.dit_head_response = "accepted"
        check_panel_invitation.dit_head_response_date = dit_head_response_date

        check_panel_invitation.panel_response = "pending"

        check_panel_invitation.save()

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has accepted your Panel Invitation for Final Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        # gmail notification for Panel
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.panel_full_name + ",\n" + "You have been invited as a Panel for Final Defense on " + check_panel_invitation.research_final_defense_date + " " + check_panel_invitation.research_final_defense_start_time + " to " + check_panel_invitation.research_final_defense_end_time + "\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        get_panel_invitations = FinalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet5-final-defense-panel-invitation-dashboard")


# DIT Head - BET3 - Proposal - Panel Invitation - Decline w/ Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalPanelInvitationDeclineSignature(request, id):
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
        get_panel_invitations = FinalPanelInvitation.objects.all().filter(dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    # BET-3 - Topic - Panel Invitation
    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"
        check_panel_invitation.dit_head_signature = True

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = FinalPanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = FinalPanelInvitationLog(
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
            research_final_defense_date=check_updated_panel_invitation.research_final_defense_date,
            research_final_defense_start_time=check_updated_panel_invitation.research_final_defense_start_time,
            research_final_defense_end_time=check_updated_panel_invitation.research_final_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

        # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has declined your Panel Invitation for Final Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )


        panel_invitation_bet3_check = FinalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "panel_invitations": panel_invitation_bet3_check, 
            "declined_student_member_name": check_panel_invitation.student_leader_full_name, 
            "declined_student_member_username": check_panel_invitation.student_leader_username, 
            "response": "sweet panel invitation bet-3 declined"}

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet5-final-defense-panel-invitation-dashboard")


# DIT Head - Panel Invitation BET-5 Decline Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalPanelInvitationDecline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    dit_head_response_date = today.strftime("%B %d, %Y")

    # PANEL INVITATION BET-3
    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=int(id))

        check_panel_invitation.dit_head_response = "declined"
        check_panel_invitation.dit_head_response_date = dit_head_response_date
        check_panel_invitation.form_status = "declined - DIT Head"

        check_panel_invitation.panel_response = "None"
        check_panel_invitation.panel_response_date = "None"

        check_panel_invitation.save()

        check_updated_panel_invitation = FinalPanelInvitation.objects.get(id=int(id))

        log_bet3_panel_invitation = FinalPanelInvitationLog(
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
            research_final_defense_date=check_updated_panel_invitation.research_final_defense_date,
            research_final_defense_start_time=check_updated_panel_invitation.research_final_defense_start_time,
            research_final_defense_end_time=check_updated_panel_invitation.research_final_defense_end_time,
            form_date_sent=check_updated_panel_invitation.form_date_sent,
            form_status=check_updated_panel_invitation.form_status,
            form=check_updated_panel_invitation.form,
            subject_teacher_username=check_updated_panel_invitation.subject_teacher_username,
            subject_teacher_full_name=check_updated_panel_invitation.subject_teacher_full_name,
            is_completed=check_updated_panel_invitation.is_completed,
        )
        log_bet3_panel_invitation.save()

        check_updated_panel_invitation.delete()

          # gmail notification for Student
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + " has declined your Panel Invitation for Final Defense.\nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        panel_invitation_bet3_check = FinalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username, dit_head_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "panel_invitations": panel_invitation_bet3_check, 
            "declined_student_member_name": check_panel_invitation.student_leader_full_name, 
            "declined_student_member_username": check_panel_invitation.student_leader_username, 
            "response": "sweet panel invitation bet-3 declined"
            }

        return render(request, "dit-head-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("dit-head-bet5-final-defense-panel-invitation-dashboard")


# DIT Head - Panel Conforme BET-3 Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadPanelConformeBet3Decline(request, id):
    pass


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadAcknowledgementReceipt(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user.username, dit_head_response ="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "pending_receipt": get_pending_receipt,
    }

    return render(request, "dit-head-acknowledgement-receipt.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadAcknowledgementReceiptAcceptSignature(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Check - E-sign exist
    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        pass

    else:
        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user.username, dit_head_response ="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": date_today,
            "pending_receipt": get_pending_receipt,
            "response": "sweet no esign",
        }

        return render(request, "dit-head-acknowledgement-receipt.html", context)


    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.dit_head_response = "Accepted"
        check_receipt.dit_head_response_date = date_today
        check_receipt.dit_head_signature = True
        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(DIT Head) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user.username, dit_head_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel acknowledgement receipt accepted",
            }

        return render(request, "dit-head-acknowledgement-receipt.html", context)

    except:
        return redirect("dit-head-acknowledgement-receipt")


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadAcknowledgementReceiptAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.dit_head_response = "Accepted"
        check_receipt.dit_head_response_date = date_today
        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(DIT Head) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user.username, dit_head_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel acknowledgement receipt accepted",
            }

        return render(request, "dit-head-acknowledgement-receipt.html", context)

    except:
        return redirect("dit-head-acknowledgement-receipt")


# DIT Head - BET-3 Panel Invitation Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
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


# DIT Head - BET-3 Adviser Conforme Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET3AdviserConformeLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = AdviserConforme.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    get_panel_invitation_2 = AdviserConformeLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "dit-head-bet3-adviser-conforme-logs.html", context)


# DIT Head - BET-3 Panel Invitation Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET3ProposalPanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = ProposalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    get_panel_invitation_2 = ProposalPanelInvitationLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "dit-head-bet3-proposal-panel-invitation-logs.html", context)

# DIT Head
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadPanelConformeLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_conforme = PanelConforme.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    get_panel_conforme_2 = PanelConformeLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_conforme": get_panel_conforme,
        "panel_conforme_2": get_panel_conforme_2,
    }

    return render(request, "dit-head-panel-conforme-logs.html", context)


# DIT Head
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5FinalPanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = FinalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    get_panel_invitation_2 = FinalPanelInvitationLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "dit-head-bet5-final-panel-invitation-logs.html", context)

# DIT Head
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadBET5AcknowledgementReceiptLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_accepted_receipt = AcknowledgementReceipt.objects.all().filter(dit_head_username = currently_loggedin_user.username, dit_head_response ="Accepted")


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "accepted_receipt": get_accepted_receipt,
    }

    return render(request, "dit-head-acknowledgement-receipt-logs.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_department_head, login_url="login")
def ditHeadTheDevs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    # get_panel_invitation = FinalPanelInvitation.objects.all().filter(dit_head_username=currently_loggedin_user.username)
    # get_panel_invitation_2 = FinalPanelInvitationLog.objects.all().filter(dit_head_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        # "panel_invitations": get_panel_invitation,
        # "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "dit-head-the-devs.html", context)

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