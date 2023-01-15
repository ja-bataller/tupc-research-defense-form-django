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

today = date.today()
date_today = today.strftime("%B %d, %Y")

# Panel - Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
    
    get_today_final_defense = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_final_defense_date=date_today, form_status="accepted", panel_attendance="")
    get_today_final_defense_present = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, research_final_defense_date=date_today, form_status="accepted", panel_attendance="present")

    # Get Student Leader Data
    try:
        get_student_final_defense_data = StudentLeader.objects.get(username=get_today_final_defense.student_leader_username)
    except:
        get_student_final_defense_data = None

    try:
        get_completed_final_defense = DefenseSchedule.objects.get(student_leader_username=get_student_final_defense_data.username, name=get_student_final_defense_data.bet5_subject_teacher_name, form="Research Final Defense", date=date_today, status="Completed")
    except:
        get_completed_final_defense = None

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

        "today_final_defense": get_today_final_defense,
        "today_final_defense_present": get_today_final_defense_present,
        "completed_final_defense": get_completed_final_defense,
    }

    return render(request, "panel-dashboard.html", context)


# Panel - Research Title Defense Day Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelTitleDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if get_student_leader_data.research_title_defense_date != date_today:
        return redirect("panel-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    get_research_titles = TitleVote.objects.all().filter(student_leader_username=id, panel_username=currently_loggedin_user.username, panel_response_date = date_today)

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
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Revise Title")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelTitleDefenseDayLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelTitleDefenseDayAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if get_student_leader_data.research_proposal_defense_date != date_today:
        return redirect("panel-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    get_present_panel_members_proposal_defense = ProposalDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
        pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass


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

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
       pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass

    get_end_voting = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = get_student_leader_data.bet3_subject_teacher_username, start_voting = 1, end_voting = 1)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,

        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "accepted_research_title": research_title,
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
        "get_accepted_research_title": get_accepted_research_title,
        "end_voting": get_end_voting,
    }

    return render(request, "panel-bet3-proposal-defense-day.html", context)


# Panel - BET-3 - Proposal Defense - Panel Chairman attach signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayPanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDaySaveCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
    
    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
       pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
       pass

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

                research_title = research_title,
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayDeleteCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayCritiquePanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayCritiquePanelAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayCritiquePanelChairmanLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayCritiquePanelLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayDeferred(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayNotAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        ProposalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, proposal_defense_response="").update(proposal_defense_response = "Not Accepted")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayPanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayPanelAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayPanelChairmanLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseDayPanelLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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


# Panel - Research Final Defense Day Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDay(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    if get_student_leader_data.research_final_defense_date != date_today:
        return redirect("panel-dashboard")

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    get_present_panel_members_proposal_defense = FinalDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
        pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass


    try:
        check_start_voting = FinalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1)
    except:
        check_start_voting = 0
    
    try:
        check_pending_pc_panel_defense_signature = FinalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1, panel_chairman_signature_response = False)
    except:
        check_pending_pc_panel_defense_signature = 0

    get_end_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = get_student_leader_data.bet5_subject_teacher_username, start_voting = 1, end_voting = 1)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,

        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "research_title": research_title,
        "get_accepted_research_title": get_accepted_research_title,
        # "research_titles": get_research_titles,
        # "panel_members": get_panel_members,
        # "present_panel_members": get_present_panel_members,
        # "absent_panel_members": get_absent_panel_members,
        # "current_panel_title_defense": get_current_panel_title_defense,
        "present_panel_members_proposal_defense": get_present_panel_members_proposal_defense,
        # "panel_chairman": get_panel_chairman,
        # "check_panel_complete_response": check_panel_complete_response,
        # "check_panel_mark_done": check_panel_mark_done,
        # "research_title_data": get_research_title_data,
        # "research_title_accepted": get_research_title_accepted,
        # "research_title_revise": get_research_title_revise,
        "start_voting": check_start_voting,
        "student_username": id,
        "end_voting": get_end_voting,

        # "response_signature": get_no_response_signature
    }

    return render(request, "panel-bet5-final-defense-day.html", context)


# Panel - BET-5 - Final Defense - Accepted with Revision
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        FinalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, final_defense_response="").update(final_defense_response = "Accepted with Revision")

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
            "response": "sweet final defense accepted with revision"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")
    

# Panel - BET-3 - Proposal Defense - Deferred with Revision
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayDeferred(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        FinalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, final_defense_response="").update(final_defense_response = "Deferred with Revision")

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
            "response": "sweet final defense deferred with revision"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")


# Panel - BET-3 - Proposal Defense - Not Accepted
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayNotAccepted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        FinalDefenseForm.objects.filter(student_leader_username=id, panel_username = request.user, start_voting=True, final_defense_response="").update(final_defense_response = "Not Accepted")

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
            "response": "sweet final defense not accepted"
        }

        return render(request, "panel-dashboard.html", context)

    except:
        return redirect("panel-dashboard")


# Panel - BET-5 - Final Defense Form - Panel Chairman attach signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayPanelChairmanAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
            "response": "sweet final defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    

    try:
        FinalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)\
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
        "response": "sweet final panel chairman esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-5 - Final Defense Form - Panel attach signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayPanelAttachSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
            "response": "sweet final defense no esign"
        }

        return render(request, "panel-dashboard.html", context)
    

    try:
        FinalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)\
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
        "response": "sweet final panel esign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-5 - Final Defense Form -  Panel Chairman live signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayPanelChairmanLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        FinalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, is_panel_chairman =  True, panel_chairman_signature_response = False)\
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
        "response": "sweet final panel chairman live sign"
    }

    return render(request, "panel-dashboard.html", context)


# Panel - BET-5 - Final Defense Form -  Panel Chairman live signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseDayPanelLiveSignature(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        FinalDefenseForm.objects.filter(student_leader_username = id, panel_username=currently_loggedin_user.username, panel_signature_response = False)\
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
        "response": "sweet final panel live sign"
    }

    return render(request, "panel-dashboard.html", context)



# Panel - Profile Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("panel-profile")


# Panel - Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelCreateESignature(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
                    return render(request, "login.html", context)

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Topic Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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

# PANEL - PANEL CONFORME

# Panel - BET3 - Panel Conforme - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelPanelConformeDashboard(request):
    currently_loggedin_user = request.user
    print("Current User:", currently_loggedin_user.username)

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]


    get_panel_conforme = PanelConforme.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "get_panel_conforme": get_panel_conforme}

    return render(request, "panel-panel-conforme.html", context)


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelPanelConformeAcceptSignature(request, id):
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
        get_panel_conforme = PanelConforme.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_conforme,
            "response": "sweet no esign",
        }

        return render(request, "panel-panel-conforme.html", context)

    try:
        check_panel_conforme = PanelConforme.objects.get(id=id)

        check_panel_conforme.panel_response = "Accepted"
        check_panel_conforme.panel_response_date = response_date
        check_panel_conforme.panel_signature = True

        check_panel_conforme.form_status = "Accepted"
        check_panel_conforme.is_completed = True
        check_panel_conforme.save()


        # Send g-mail notifications
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.student_leader_full_name + ",\n" + check_panel_conforme.panel_full_name + " has accepted your Panel Conforme for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_panel_conforme = PanelConforme.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "get_panel_conforme": get_panel_conforme,
            "accepted_student_member_name": check_panel_conforme.student_leader_full_name,
            "accepted_student_member_username": check_panel_conforme.student_leader_username,
            "response": "sweet panel conforme accepted",
        }

        return render(request, "panel-panel-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-conforme")


# Panel - Panel Conforme - Accept with Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelPanelConformeAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")


    try:
        check_panel_conforme = PanelConforme.objects.get(id=id)

        check_panel_conforme.panel_response = "Accepted"
        check_panel_conforme.panel_response_date = response_date

        check_panel_conforme.form_status = "Accepted"
        check_panel_conforme.is_completed = True
        check_panel_conforme.save()


        # Send g-mail notifications
        send_mail(
            "Panel Conforme for Topic Defense",
            "Good Day " + check_panel_conforme.student_leader_full_name + ",\n" + check_panel_conforme.panel_full_name + " has accepted your Panel Conforme for Topic Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_panel_conforme = PanelConforme.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_conforme.student_leader_full_name,
            "accepted_student_member_username": check_panel_conforme.student_leader_username,
            "get_panel_conforme": get_panel_conforme,
            "response": "sweet panel conforme accepted",
        }

        return render(request, "panel-panel-conforme.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-panel-conforme")


# Panel - Research Title Defense Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def panelResearchTitleDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_panel_research_title_defense_form = TitleDefenseForm.objects.all().filter(panel_username=currently_loggedin_user.username)

    context = {"currently_loggedin_user_full_name": currently_loggedin_user_full_name, "currently_loggedin_user_account": currently_loggedin_user_account}

    return render(request, "panel-research-title-defense-dashboard.html", context)


# Panel - Panel Conforme BET-3 Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

# Panel - BET-3 Panel Invitation Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalPanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username)
    get_panel_invitation_2 = ProposalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "panel-bet3-proposal-panel-invitation-logs.html", context)

# Panel - BET-3 Panel Invitation Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalPanelInvitationLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # BET-3 Panel Invitation Logs
    get_panel_invitation = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username)
    get_panel_invitation_2 = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "panel_invitations": get_panel_invitation,
        "panel_invitations_2": get_panel_invitation_2,
    }

    return render(request, "panel-bet5-final-panel-invitation-logs.html", context)


# Panel - BET-3 Title Defense Logs
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3TitleDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

    completed_title_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)
    deferred_title_defense = ProposalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)

    absent_title_defense = ProposalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)
    absent_title_defense_log = ProposalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)

    present_reschedule_title_defense = ProposalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="present-reschedule")
    absent_reschedule_title_defense = ProposalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="absent-reschedule")

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

    return render(request, "panel-bet3-research-proposal-defense-logs.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

    completed_title_defense = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)
    deferred_title_defense = FinalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", is_completed=True)

    absent_title_defense = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)
    absent_title_defense_log = FinalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, form_status="accepted", panel_attendance="absent", is_completed=False)

    present_reschedule_title_defense = FinalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="present-reschedule")
    absent_reschedule_title_defense = FinalPanelInvitationLog.objects.all().filter(panel_username=currently_loggedin_user.username, panel_attendance="absent-reschedule")

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

    return render(request, "panel-bet5-research-final-defense-logs.html", context)

# Panel - Research Final Defense Day Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefenseLogCompleted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."

    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    get_present_panel_members_proposal_defense = FinalDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
        pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass


    try:
        check_start_voting = FinalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1)
    except:
        check_start_voting = 0
    
    try:
        check_pending_pc_panel_defense_signature = FinalDefenseForm.objects.get(student_leader_username=id, panel_username=currently_loggedin_user.username, start_voting=1, panel_chairman_signature_response = False)
    except:
        check_pending_pc_panel_defense_signature = 0

    get_end_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = get_student_leader_data.bet5_subject_teacher_username, start_voting = 1, end_voting = 1)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,

        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "research_title": research_title,
        "get_accepted_research_title": get_accepted_research_title,
        # "research_titles": get_research_titles,
        # "panel_members": get_panel_members,
        # "present_panel_members": get_present_panel_members,
        # "absent_panel_members": get_absent_panel_members,
        # "current_panel_title_defense": get_current_panel_title_defense,
        "present_panel_members_proposal_defense": get_present_panel_members_proposal_defense,
        # "panel_chairman": get_panel_chairman,
        # "check_panel_complete_response": check_panel_complete_response,
        # "check_panel_mark_done": check_panel_mark_done,
        # "research_title_data": get_research_title_data,
        # "research_title_accepted": get_research_title_accepted,
        # "research_title_revise": get_research_title_revise,
        "start_voting": check_start_voting,
        "student_username": id,
        "end_voting": get_end_voting,

        # "response_signature": get_no_response_signature
    }

    return render(request, "panel-bet5-final-defense-data.html", context)

# Panel - Research Proposal Defense Day Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET3ProposalDefenseLogCompleted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("panel-dashboard")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."


    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    get_present_panel_members_proposal_defense = ProposalDefenseForm.objects.all().filter(student_leader_username=id, panel_attendance="present")

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
        pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass


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
        get_panel_critique = ProposalDefenseCritique.objects.all().filter(student_leader_username=id, panel_username = currently_loggedin_user.username, panel_attendance="present")
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

    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
       pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass

    get_end_voting = ProposalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = get_student_leader_data.bet3_subject_teacher_username, start_voting = 1, end_voting = 1)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,

        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,
        "group_members": get_group_members,
        "accepted_research_title": research_title,
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
        "get_accepted_research_title": get_accepted_research_title,
        "end_voting": get_end_voting,
    }

    return render(request, "panel-bet3-proposal-defense-data.html", context)


# Panel - BET-3 Title Defense Log Completed
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

    if get_student_leader_data.middle_name == "":
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
        "defense_date": get_present_panel_members[0].defense_date,
        "defense_start_time": get_present_panel_members[0].defense_start_time,
        "defense_end_time": get_present_panel_members[0].defense_end_time,
    }

    return render(request, "panel-bet3-research-title-defense-data.html", context)


# Panel - BET-3 Title Defense Log Redefense
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

    if get_student_leader_data.middle_name == "":
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
        "defense_date": get_present_panel_members[0].defense_date,
        "defense_start_time": get_present_panel_members[0].defense_start_time,
        "defense_end_time": get_present_panel_members[0].defense_end_time,
    }

    return render(request, "panel-bet3-research-title-defense-data.html", context)

##### PANEL - PROPOSAL DEFENSE #####

# Panel - BET3 - Proposal Defense - Panel Invitation - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Proposal Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Proposal Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Proposal Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
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

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Proposal Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Proposal Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

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


##### PANEL - FINAL DEFENSE #####

# Panel - BET5 - Final Defense - Panel Invitation - Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalDefensePanelInvitationDashboard(request):
    currently_loggedin_user = request.user
    print("Current User:", currently_loggedin_user.username)

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # PANEL INVITATION BET-3
    get_panel_invitation = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "panel_invitations": get_panel_invitation}

    return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)


# Panel - BET5 - Final Defense - Panel Invitation - Accept with Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalPanelInvitationAcceptSignature(request, id):
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
        get_panel_invitations = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Final Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet5-final-defense-panel-invitation-dashboard")


# Panel - BET5 - Final Defense - Panel Invitation - Decline with Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalPanelInvitationDeclineSignature(request, id):
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
        get_panel_invitations = FinalPanelInvitation.objects.all().filter(panel_username=currently_loggedin_user.username, panel_response="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "panel_invitations": get_panel_invitations,
            "response": "sweet no esign",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date
        check_panel_invitation.panel_signature = True
        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Final Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet5-final-defense-panel-invitation-dashboard")


# Panel - BET5 - Final Defense - Panel Invitation - Accept Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalPanelInvitationAccept(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "accepted"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "accepted"
        check_panel_invitation.save()

        update_student_leader_data = StudentLeader.objects.get(username=check_panel_invitation.student_leader_username)
        update_student_leader_data.request_limit = int(update_student_leader_data.request_limit) - 1
        update_student_leader_data.save()

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has accepted your Panel Invitation for Final Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "accepted_student_member_name": check_panel_invitation.student_leader_full_name,
            "accepted_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 accepted",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet5-final-defense-panel-invitation-dashboard")


# Panel - BET5 - Final Defense - Panel Invitation - Decline Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelBET5FinalPanelInvitationDecline(request, id):
    currently_loggedin_user = request.user

    print(id, type(id))

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    response_date = today.strftime("%B %d, %Y")

    try:
        check_panel_invitation = FinalPanelInvitation.objects.get(id=id)

        check_panel_invitation.panel_response = "declined"
        check_panel_invitation.panel_response_date = response_date

        check_panel_invitation.form_status = "declined"
        check_panel_invitation.save()

        # Send g-mail notifications
        send_mail(
            "Panel Invitation for Final Defense",
            "Good Day " + check_panel_invitation.student_leader_full_name + ",\n" + check_panel_invitation.panel_full_name + " has declined your Panel Invitation for Final Defense. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "declined_student_member_name": check_panel_invitation.student_leader_full_name,
            "declined_student_member_username": check_panel_invitation.student_leader_username,
            "response": "sweet panel invitation bet-3 declined",
        }

        return render(request, "panel-bet5-final-defense-panel-invitation-dashboard.html", context)

    except:
        print("NO FOUND")
        return redirect("panel-bet5-final-defense-panel-invitation-dashboard")





@login_required(login_url="login")
@user_passes_test(lambda u: u.is_panel, login_url="login")
def panelTheDevs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "panel-the-devs.html", context)


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