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

# Subject Teacher - Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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

    if get_student_leader_data.middle_name == "":
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
        check_accepted_title = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Accepted")
        final_research_title = check_accepted_title.research_title
    except:
        check_accepted_title = None

    try:
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, status="Title Defense - Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Revise Title")
        final_research_title = get_research_title_revise.research_title
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
        check_title_defense_completed = DefenseSchedule.objects.get(student_leader_username=id, form="Research Title Defense", date=date_today, status="Completed")
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

        for i in range(len(get_present_panel_members)):
            save_topic_panel_conforme = PanelConforme(
                student_leader_username = get_present_panel_members[i].student_leader_username,
                student_leader_full_name = get_present_panel_members[i].student_leader_full_name,
                course_major_abbr = get_present_panel_members[i].course_major_abbr,
                
                dit_head_username = get_present_panel_members[i].dit_head_username,
                dit_head_full_name = get_present_panel_members[i].dit_head_full_name,
                dit_head_response = "pending",

                panel_username = get_present_panel_members[i].panel_username,
                panel_full_name = get_present_panel_members[i].panel_full_name,
                panel_response = "on hold",

                research_title = final_research_title,
                defense_date = get_present_panel_members[i].research_title_defense_date,
                defense_start_time = get_present_panel_members[i].research_title_defense_start_time,
                defense_end_time = get_present_panel_members[i].research_title_defense_end_time,

                form_date_sent = date_today,

                form_status = "pending",
                form = "Topic Panel Conforme",

                subject_teacher_username = get_present_panel_members[i].subject_teacher_username,
                subject_teacher_full_name = get_present_panel_members[i].subject_teacher_full_name,
            )
            save_topic_panel_conforme.save()
             # Send g-mail notifications
            send_mail(
                "Topic Defense - Panel Conforme",
                "Good Day " + get_present_panel_members[i].dit_head_full_name + ",\n" + get_present_panel_members[i].student_leader_full_name + " needs an approval for their Topic Defense Panel Conforme. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )
            i + 1

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
            panel_response_date = date_today
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherTitleDefenseDayStartVote(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherTitleDefenseDayCloseVote(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Subject Teacher - Get Subject Teacher Data
    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
            update_research_title_data_4.save()

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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

    if get_student_leader_data.middle_name == "":
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
        research_title = get_accepted_research_title.research_title
    except:
       pass
    
    try:
        get_revise_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
        research_title = get_revise_research_title.research_title
    except:
        pass
    
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

        "accepted_research_title": research_title,
        "get_accepted_research_title": get_accepted_research_title,

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseDayStartCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
            
            research_title = research_title
            )
        save_critique.save()

        i + 1

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseDayEndCritique(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


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
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseDayStartVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


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
        return redirect("login")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseDayEndVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


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
        accepted_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted");
        revise_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title");

        if accepted_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(proposal_defense_status = "Accepted with Revision", status = "Proposal Defense - Accepted with Revision")
        
        if revise_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title").update(proposal_defense_status = "Accepted with Revision", status = "Proposal Defense - Accepted with Revision")

    elif int(deferred_with_revision_count) >= 3:
        print("Deferred with Revision - Redefense")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Deferred with Revision"
            get_student_proposal_defense_form[i].end_voting = True
            get_student_proposal_defense_form[i].save()
            i + 1
        
        ProposalDefenseCritique.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username).update(form_status = "completed")
        accepted_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted");
        revise_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title");

        if accepted_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(proposal_defense_status = "Deferred with Revision", status = "Proposal Defense - Deferred with Revision")
        
        if revise_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title").update(proposal_defense_status = "Deferred with Revision", status = "Proposal Defense - Deferred with Revision")
    
    elif int(not_accepted_count) >= 3:
        print("Not Accepted")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Not Accepted"
            get_student_proposal_defense_form[i].end_voting = True
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseDayEndDefense(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

    
    get_present_panel_members = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present")


    try:
        get_student_research_title = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        get_student_research_title = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
    
    if get_student_research_title.proposal_defense_status == "Accepted with Revision":
        DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Proposal Defense").update(status = "Completed")
        StudentLeader.objects.filter(username=id).update(bet3_status = "Completed", bet5_status = "Ongoing", bet3_proposal_defense_status = "completed", request_limit = 5)
        ProposalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present").update(is_completed = True)
        
        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")
        
        for i in range(len(get_present_panel_members)):
            save_topic_panel_conforme = PanelConforme(
                student_leader_username = get_present_panel_members[i].student_leader_username,
                student_leader_full_name = get_present_panel_members[i].student_leader_full_name,
                course_major_abbr = get_present_panel_members[i].course_major_abbr,
                
                dit_head_username = get_present_panel_members[i].dit_head_username,
                dit_head_full_name = get_present_panel_members[i].dit_head_full_name,
                dit_head_response = "pending",

                panel_username = get_present_panel_members[i].panel_username,
                panel_full_name = get_present_panel_members[i].panel_full_name,
                panel_response = "on hold",

                research_title = get_student_research_title.research_title,
                defense_date = get_present_panel_members[i].research_proposal_defense_date,
                defense_start_time = get_present_panel_members[i].research_proposal_defense_start_time,
                defense_end_time = get_present_panel_members[i].research_proposal_defense_end_time,

                form_date_sent = date_today,

                form_status = "pending",
                form = "Proposal Panel Conforme",

                subject_teacher_username = get_present_panel_members[i].subject_teacher_username,
                subject_teacher_full_name = get_present_panel_members[i].subject_teacher_full_name,
            )
            save_topic_panel_conforme.save()

             # Send g-mail notifications
            send_mail(
                "Proposal Defense - Panel Conforme",
                "Good Day " + get_present_panel_members[i].dit_head_full_name + ",\n" + get_present_panel_members[i].student_leader_full_name + " needs an approval for their Proposal Defense Panel Conforme. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
                "unofficial.tupc.uitc@gmail.com",
                ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
                fail_silently=False,
            )
            i + 1
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

        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

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
        get_student_adviser_conforme = AdviserConforme.objects.filter(student_leader_username=id)
        get_student_proposal_panel_invitation = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Proposal Defense Panel Invitation", research_proposal_defense_date=date_today, panel_attendance="present")
        get_student_proposal_defense_schedule = DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Proposal Defense")
        get_student_proposal_defense_forms = ProposalDefenseForm.objects.all().filter(student_leader_username=id, subject_teacher_username = request.user, defense_date=date_today)

        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

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

        # Adviser Conforme Log
        for i in range(len(get_student_adviser_conforme)):
            log_adviser_conforme = AdviserConformeLog(
                student_leader_username = get_student_adviser_conforme[i].student_leader_username,
                student_leader_full_name = get_student_adviser_conforme[i].student_leader_full_name,
                course = get_student_adviser_conforme[i].course,

                research_title = get_student_adviser_conforme[i].research_title,

                form_date_submitted = get_student_adviser_conforme[i].form_date_submitted,

                dit_head_username = get_student_adviser_conforme[i].dit_head_username,
                dit_head_name = get_student_adviser_conforme[i].dit_head_name,
                dit_head_response = get_student_adviser_conforme[i].dit_head_response,
                dit_head_response_date = get_student_adviser_conforme[i].dit_head_response_date,
                dit_head_signature = get_student_adviser_conforme[i].dit_head_signature,

                adviser_username = get_student_adviser_conforme[i].adviser_username,
                adviser_name = get_student_adviser_conforme[i].adviser_name,
                adviser_response = get_student_adviser_conforme[i].adviser_response,
                adviser_response_date = get_student_adviser_conforme[i].adviser_response_date,
                adviser_signature = get_student_adviser_conforme[i].adviser_signature,

                form_status = get_student_adviser_conforme[i].form_status,
            )
            log_adviser_conforme.save()
            i + 1
        print("Adviser Conforme - Log - Successfully")

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
        get_student_title_defense_form.delete()
       
        get_student_proposal_panel_invitation.delete()
        get_student_proposal_defense_schedule.delete()
        get_student_proposal_defense_forms.delete()

        get_adviser_data = User.objects.filter(username=get_student_adviser_conforme[0].adviser_username)
        get_adviser_data.update(advisee_count = get_adviser_data - 1)
        get_student_adviser_conforme.delete()
        
        StudentLeader.objects.filter(username=id).update(
            request_limit = 5, 

            research_titles_status = "",
            bet3_panel_invitation_status = "",
            title_defense_status = "",
            research_title_defense_date ="", 
            research_title_defense_start_time = "", 
            research_title_defense_end_time = "",

            adviser_username = "",
            adviser_name = "",
            adviser_conforme_status = "",

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
        

# SUBJECT TEACHER - FINAL DEFENSE PROCESS
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseDay(request, id):

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

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."
    print("Student Leader Full Name: ", student_leader_full_name)
    # ----- Student Leader Data -----


    # ----- Validation ------

    # If Student Defense Schedule and Date Today is not the same
    if get_student_leader_data.research_final_defense_date != date_today:
        return redirect("subject-teacher-dashboard")
    
     # ----- Validation ------

    # ----- Fetch Data -----
    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id) # Get all the group members

    get_panel_members  = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="")

    get_present_panel_members = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present")
    get_pending_proposal_defense = FinalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present", is_completed = False)

    get_absent_panel_members = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="absent")
    
    get_bet3_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=id)

    get_proposal_defense_present_panel = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")

    get_present_panel_members_proposal_defense = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, panel_attendance="present")

    get_start_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user)

    get_end_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user)

    check_pending = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user)
    
    check_pending_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user)

    get_start_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1)

    get_end_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, end_voting = 1)

    check_pending_vote = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, final_defense_response = "")

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
        get_student_proposal_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, form="Research Final Defense", date=date_today, status="Reserved")
    except:
        pass
    
    try:
        get_panel_chairman = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, panel_attendance="present", is_panel_chairman=1)
        print("Panel Chairman: ", get_panel_chairman.panel_full_name)
    except:
        get_panel_chairman = None

    try:
        get_pending_panel_chairman_signature_response = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, panel_chairman_signature_response = 1)
    except:
        get_pending_panel_chairman_signature_response = 0
    
    try:
        get_done_pc_sign = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_pc_sign = None

    try:
        get_done_p_sign = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_p_sign = None


    all_pending_panel_signature_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = request.user, start_voting = 1, panel_signature_response = False)
    
     # ----- Fetch Data -----

    if not get_panel_members:
        if get_present_panel_members.count() < 3:
            print("Re Schedule")

            get_student_proposal_defense_schedule.status = "Reschedule"
            get_student_proposal_defense_schedule.save()

            # Get Updated Defense Schedule
            try:
                updated_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, form="Research Final Defense", date=date_today, status="Reschedule")

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
                log_panel_invitation = FinalPanelInvitationLog(
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
                    research_final_defense_date=get_bet3_panel_invitations[i].research_final_defense_date,
                    research_final_defense_start_time=get_bet3_panel_invitations[i].research_final_defense_start_time,
                    research_final_defense_end_time=get_bet3_panel_invitations[i].research_final_defense_end_time,
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
                log_research_proposal_defense = FinalDefenseFormLog(
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

            get_student_leader_data.research_final_defense_date = ""
            get_student_leader_data.research_final_defense_start_time = ""
            get_student_leader_data.research_final_defense_end_time = ""
            get_student_leader_data.request_limit = 5
            get_student_leader_data.bet5_final_defense_panel_invitation_status = ""
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

        "accepted_research_title": research_title,

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
        "get_accepted_research_title_data": get_accepted_research_title,
    }

    return render(request, "subject-teacher-bet5-final-defense-day.html", context)


# Subject Teacher - Research Final Defense Day - Present Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefensePresent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = FinalPanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    try:
        get_student_leader_data = StudentLeader.objects.get(username=get_panel_invitation_data.student_leader_username)
    except:
        return redirect("subject-teacher-dashboard")

    get_panel_invitation_data.panel_attendance = "present"
    get_panel_invitation_data.save()

    save_proposal_defense_form = FinalDefenseForm(
        student_leader_username=get_panel_invitation_data.student_leader_username,
        student_leader_full_name=get_panel_invitation_data.student_leader_full_name,
        course_major_abbr=get_panel_invitation_data.course_major_abbr,

        panel_username=get_panel_invitation_data.panel_username,
        panel_full_name=get_panel_invitation_data.panel_full_name,
        panel_attendance="present",

        form_date=get_panel_invitation_data.research_final_defense_date,
        form="Research Final Defense",

        subject_teacher_username=get_student_leader_data.bet5_subject_teacher_username,
        subject_teacher_full_name=get_student_leader_data.bet5_subject_teacher_name,

        defense_date=get_student_leader_data.research_final_defense_date,
        defense_start_time=get_student_leader_data.research_final_defense_start_time,
        defense_end_time=get_student_leader_data.research_final_defense_end_time,
    )
    save_proposal_defense_form.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet final defense present panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Final Defense Day - Absent Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseAbsent(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_panel_invitation_data = FinalPanelInvitation.objects.get(id=id)
    except:
        return redirect("subject-teacher-dashboard")

    get_panel_invitation_data.panel_attendance = "absent"
    get_panel_invitation_data.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet final defense absent panel",
        "panel_invitation_data": get_panel_invitation_data,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Final Defense Day - Set Panel Chairman Process
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseDaySetPanelChairman(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    save_panel_chairman = FinalDefenseForm.objects.get(id=id)
    save_panel_chairman.is_panel_chairman = True
    save_panel_chairman.save()

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "response": "sweet final defense panel chairman assigned",
        "panel_chairman_data": save_panel_chairman,
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research FInal Defense Day - Start Voting
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseDayStartVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    get_done_signature_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)

    for i in range(len(get_done_signature_response)):
        get_done_signature_response[i].start_voting = True
        get_done_signature_response[i].save()

        i + 1

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")

    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet final defense start voting",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Final Defense Day - End Voting
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseDayEndVoting(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


    get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
    get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

    
    get_accepted_panel_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, final_defense_response = "Accepted with Revision")
    get_deferred_panel_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, final_defense_response = "Deferred with Revision")
    get_not_accepted_panel_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username, final_defense_response = "Not Accepted")

    get_student_proposal_defense_form = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=date_today, subject_teacher_username = currently_loggedin_user.username)
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

        accepted_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted");
        revise_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title");

        if accepted_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(final_defense_status = "Accepted with Revision", status = "Final Defense - Accepted with Revision")
        
        if revise_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title").update(final_defense_status = "Accepted with Revision", status = "Final Defense - Accepted with Revision")

    elif int(deferred_with_revision_count) >= 3:
        print("Deferred with Revision - Redefense")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Deferred with Revision"
            get_student_proposal_defense_form[i].end_voting = True
            get_student_proposal_defense_form[i].save()
            i + 1
        
        accepted_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted");
        revise_research_title = ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title");

        if accepted_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(final_defense_status = "Deferred with Revision", status = "Final Defense - Deferred with Revision")
        
        if revise_research_title:
            ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Revise Title").update(final_defense_status = "Deferred with Revision", status = "Final Defense - Deferred with Revision")
    
    elif int(not_accepted_count) >= 3:
        print("Not Accepted")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].form_status = "Not Accepted"
            get_student_proposal_defense_form[i].end_voting = True
            get_student_proposal_defense_form[i].save()
            i + 1
        
        ResearchTitle.objects.filter(student_leader_username = id, title_defense_status = "Accepted").update(final_defense_status = "Not Accepted", status = "Final Defense - Not Accepted")

    elif accepted_with_revision_count == deferred_with_revision_count or accepted_with_revision_count == not_accepted_count or deferred_with_revision_count == not_accepted_count:
        print("Tie - re-vote")
        for i in range(len(get_student_proposal_defense_form)):
            get_student_proposal_defense_form[i].final_defense_response = None
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
        "response": "sweet final defense vote tie",
        }

        return render(request, "subject-teacher-dashboard.html", context)
    

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "subject_teacher_data": get_subject_teacher_data,
        "today_defense_schedule": get_today_defense_schedule,
        "completed_today_defense_schedule": get_completed_today_defense_schedule,
        "student_leader_username": id,
        "response": "sweet final defense end voting",
    }

    return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - Research Final Defense Day - End Defense
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseDayEndDefense(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        get_subject_teacher_data = User.objects.get(username=currently_loggedin_user.username)
    except:
        return redirect("login")


    try:
        get_student_research_title = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
    except:
        get_student_research_title = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Revise Title")
    
    if get_student_research_title.final_defense_status == "Accepted with Revision":
        DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Final Defense").update(status = "Completed")
        StudentLeader.objects.filter(username=id).update(bet5_final_defense_status = "completed", request_limit = 5)
        FinalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present").update(is_completed = True)
        
        get_present_panel_members = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present")
        for i in range(len(get_present_panel_members)):
            save_topic_panel_conforme = PanelConforme(
                student_leader_username = get_present_panel_members[i].student_leader_username,
                student_leader_full_name = get_present_panel_members[i].student_leader_full_name,
                course_major_abbr = get_present_panel_members[i].course_major_abbr,
                
                dit_head_username = get_present_panel_members[i].dit_head_username,
                dit_head_full_name = get_present_panel_members[i].dit_head_full_name,
                dit_head_response = "pending",

                panel_username = get_present_panel_members[i].panel_username,
                panel_full_name = get_present_panel_members[i].panel_full_name,
                panel_response = "on hold",

                research_title = get_student_research_title.research_title,
                defense_date = get_present_panel_members[i].research_final_defense_date,
                defense_start_time = get_present_panel_members[i].research_final_defense_start_time,
                defense_end_time = get_present_panel_members[i].research_final_defense_end_time,

                form_date_sent = date_today,

                form_status = "pending",
                form = "Final Panel Conforme",

                subject_teacher_username = get_present_panel_members[i].subject_teacher_username,
                subject_teacher_full_name = get_present_panel_members[i].subject_teacher_full_name,
            )
            save_topic_panel_conforme.save()
            i + 1

        # Send g-mail notifications
        send_mail(
            "Final Defense - Panel Conforme",
            "Good Day " + get_present_panel_members[i].dit_head_full_name + ",\n" + get_present_panel_members[i].student_leader_full_name + " needs an approval for their Final Defense Panel Conforme. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,
        )

        try:
            get_dit_head = User.objects.get(is_department_head = 1)

            if get_dit_head.middle_name == "":
                dit_head_full_name = get_dit_head.honorific + " " + get_dit_head.first_name + " " + get_dit_head.last_name + " " + get_dit_head.suffix
            else:
                dit_head_full_name = get_dit_head.honorific + " " + get_dit_head.first_name + " " + get_dit_head.middle_name[0] + ". " + get_dit_head.last_name + " " + get_dit_head.suffix
        except:
            pass

          # ----- Student Leader Data -----
        try:
            get_student_leader_data = StudentLeader.objects.get(username=id)
            print("Student Leader: ", get_student_leader_data.username)
        except:
            return redirect("subject-teacher-dashboard")

        create_acknowledgement_receipt = AcknowledgementReceipt(
            student_leader_username = get_student_research_title.student_leader_username,
            student_leader_full_name = get_student_research_title.student_leader_name,
            course_major_abbr = get_student_research_title.course_major_abbr,

            research_title = get_student_research_title.research_title,

            dit_head_username= get_dit_head.username,
            dit_head_full_name = dit_head_full_name,
            dit_head_response = "pending",

            adaa_response = "pending",
            library_response = "pending",
            research_ext_response = "pending",

            adviser_username = get_student_leader_data.adviser_username,
            adviser_full_name = get_student_leader_data.adviser_name,
            adviser_response = "pending",

            subject_teacher_username = get_student_leader_data.bet5_subject_teacher_username,
            subject_teacher_full_name = get_student_leader_data.bet5_subject_teacher_name,
            subject_teacher_response = "pending",
        )
        create_acknowledgement_receipt.save()


        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet final defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)

    elif get_student_research_title.final_defense_status == "Deferred with Revision":
        get_student_proposal_panel_invitation = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present")
        get_student_proposal_defense_schedule = DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Final Defense")
        get_student_proposal_defense_forms = FinalDefenseForm.objects.all().filter(student_leader_username=id, subject_teacher_username = request.user, defense_date=date_today)

        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

        # Proposal Panel Invitation Logs
        for i in range (len(get_student_proposal_panel_invitation)):
            log_proposal_panel_invitation = FinalPanelInvitationLog(
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

                research_final_defense_date = get_student_proposal_panel_invitation[i].research_final_defense_date,
                research_final_defense_start_time = get_student_proposal_panel_invitation[i].research_final_defense_start_time,
                research_final_defense_end_time = get_student_proposal_panel_invitation[i].research_final_defense_end_time,

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

                start_voting = get_student_proposal_defense_forms[i].start_voting ,
                end_voting = get_student_proposal_defense_forms[i].end_voting ,

                form_status = get_student_proposal_defense_forms[i].form_status ,
                form = get_student_proposal_defense_forms[i].form ,

                subject_teacher_username = get_student_proposal_defense_forms[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_defense_forms[i].subject_teacher_full_name,

                defense_date = get_student_proposal_defense_forms[i].defense_date,
                defense_start_time = get_student_proposal_defense_forms[i].defense_start_time,
                defense_end_time = get_student_proposal_defense_forms[i].defense_end_time,
            )
            log_proposal_defense_form.save()
            i + 1
        print("Proposal Defense Forms - Log - Successfully")

        get_student_proposal_panel_invitation.delete()
        get_student_proposal_defense_schedule.delete()
        get_student_proposal_defense_forms.delete()
        StudentLeader.objects.filter(username=id).update(bet5_final_defense_panel_invitation_status = "", request_limit = 5, research_final_defense_date ="", research_final_defense_start_time = "", research_final_defense_end_time = "")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet final defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)

    elif get_student_research_title.proposal_defense_status == "Not Accepted":
        get_student_proposal_panel_invitation = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=date_today, panel_attendance="present")
        get_student_proposal_defense_schedule = DefenseSchedule.objects.filter(username = request.user, student_leader_username=id, form = "Research Final Defense")
        get_student_proposal_defense_forms = FinalDefenseForm.objects.all().filter(student_leader_username=id, subject_teacher_username = request.user, defense_date=date_today)

        get_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Reserved")
        get_completed_today_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, date=date_today, status="Completed")

        # Proposal Panel Invitation Logs
        for i in range (len(get_student_proposal_panel_invitation)):
            log_proposal_panel_invitation = FinalPanelInvitationLog(
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

                research_final_defense_date = get_student_proposal_panel_invitation[i].research_final_defense_date,
                research_final_defense_start_time = get_student_proposal_panel_invitation[i].research_final_defense_start_time,
                research_final_defense_end_time = get_student_proposal_panel_invitation[i].research_final_defense_end_time,

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

                start_voting = get_student_proposal_defense_forms[i].start_voting ,
                end_voting = get_student_proposal_defense_forms[i].end_voting ,

                form_status = get_student_proposal_defense_forms[i].form_status ,
                form = get_student_proposal_defense_forms[i].form ,

                subject_teacher_username = get_student_proposal_defense_forms[i].subject_teacher_username,
                subject_teacher_full_name = get_student_proposal_defense_forms[i].subject_teacher_full_name,

                defense_date = get_student_proposal_defense_forms[i].defense_date,
                defense_start_time = get_student_proposal_defense_forms[i].defense_start_time,
                defense_end_time = get_student_proposal_defense_forms[i].defense_end_time,
            )
            log_proposal_defense_form.save()
            i + 1
        print("Proposal Defense Forms - Log - Successfully")

        get_student_proposal_panel_invitation.delete()
        get_student_proposal_defense_schedule.delete()
        get_student_proposal_defense_forms.delete()
        
        StudentLeader.objects.filter(username=id).update(bet5_subject_teacher_username = "", bet5_subject_teacher_name = "", bet5_final_defense_panel_invitation_status = "", request_limit = 5, research_final_defense_date ="", research_final_defense_start_time = "", research_final_defense_end_time = "")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": today.strftime("%B %d, %Y"),
            "subject_teacher_data": get_subject_teacher_data,
            "today_defense_schedule": get_today_defense_schedule,
            "completed_today_defense_schedule": get_completed_today_defense_schedule,

            "response": "sweet final defense done",
        }

        return render(request, "subject-teacher-dashboard.html", context)


# Subject Teacher - BET-3 Students Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3Students(request):
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
            all_ongoing_bet3_students = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, bet3_status = "Ongoing")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "all_ongoing_bet3_students": all_ongoing_bet3_students,
            }

            return render(request, "subject-teacher-bet3-students.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-bet3-students.html", context)


# Subject Teacher - BET-3 Students Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherStudentsData(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        student_leader_data = StudentLeader.objects.get(username = id)
    except:
        pass

    try:
        group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)
    except:
        pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data":student_leader_data,
        "group_members": group_members,
    }

    return render(request, "subject-teacher-student-data.html", context)


# Subject Teacher - BET-5 Students Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5Students(request):
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
            all_ongoing_bet5_students = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, bet5_status = "Ongoing")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "all_ongoing_bet5_students": all_ongoing_bet5_students,
            }

            return render(request, "subject-teacher-bet5-students.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-bet5-students.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherLogsStudents(request):
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
            bet3_students = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, bet3_status = "Completed")

        except:
            bet3_students = ""

        try:
            bet5_students = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, bet5_status = "Completed")

        except:
            bet5_students = ""
        
        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "course_handled_list": course_handled_list,
            "bet3_students": bet3_students,
            "bet5_students": bet5_students,
        }

        return render(request, "subject-teacher-logs-students.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-logs-students.html", context)

# Subject Teacher - User Profile -  Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherCreateESignature(request):
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

        return redirect("subject-teacher-profile")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": today.strftime("%B %d, %Y"),
        "panel_data": get_panel_data,
    }

    return render(request, "subject-teacher-signature-pad.html", context)


# Subject Teacher - Remove E-Signature
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherDeleteESignature(request):
    currently_loggedin_user = request.user

    if os.path.exists("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png"):
        os.remove("uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/" + str(currently_loggedin_user) + ".png")
        return redirect("subject-teacher-profile")


# Subject Teacher - Acount Settings Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
                    return render(request, "login.html", context)

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


# Subject Teacher
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherResearchTitles(request):
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

    return render(request, "subject-teacher-research-titles.html", context)

##### SUBJECT TEACHER - BET-3 - TOPIC DEFENSE #####

# Subject Teacher - Research Title Defense Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Title Defense", course=course_input, status="Reserved")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Title Defense", course=course_input, status="Reserved")
            student_defense_unscheduled = StudentLeader.objects.all().filter(bet3_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, research_title_defense_date="")

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
            DefenseSchedule.objects.get(username=currently_loggedin_user.username, date=py_date, start_time=start_time, end_time=end_time)

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "course_handled_list": course_handled_list, 
                "response": "scheduled date exist"}

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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3TitleDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_completed_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Title Defense", status="Completed")
    get_redefense_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Title Defense", status="Re-Defense")
    get_reschedule_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Title Defense", status="Reschedule")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "completed_defense_schedule": get_completed_defense_schedule,
        "redefense_defense_schedule": get_redefense_defense_schedule,
        "reschedule_defense_schedule": get_reschedule_defense_schedule,
    }

    return render(request, "subject-teacher-bet3-research-title-defense-logs.html", context)


# Subject Teacher - BET-3 Research Title Defense Completed Logs Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
        get_research_title_accepted = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Accepted")
    except:
        get_research_title_accepted = None

    try:
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Revise Title")
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
        "absent_panel_members": get_absent_panel_members}

    return render(request, "subject-teacher-bet3-research-title-defense-data.html", context)


# Subject Teacher - BET-3 Research Title Defense Redefense Logs Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
        get_research_title_revise = ResearchTitle.objects.get(student_leader_username=id, title_defense_status="Revise Title")
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


# Subject Teacher - BET-3 Research Title Defense Logs Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_completed_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Proposal Defense", status="Completed")
    get_redefense_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Proposal Defense", status="Re-Defense")
    get_reschedule_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Proposal Defense",status="Reschedule")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "completed_defense_schedule": get_completed_defense_schedule,
        "redefense_defense_schedule": get_redefense_defense_schedule,
        "reschedule_defense_schedule": get_reschedule_defense_schedule,
    }

    return render(request, "subject-teacher-bet3-research-proposal-defense-logs.html", context)


# Subject Teacher - BET-3 Research Title Defense Completed Logs Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3ProposalDefenseLogCompleted(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    # Get Student Leader Data
    try:
        get_student_leader_data = StudentLeader.objects.get(username=id)
    except:
        return redirect("subject-teacher-bet3-title-defense-logs")
    
    try:
        get_accepted_research_title  = ResearchTitle.objects.get(student_leader_username = id, title_defense_status = "Accepted")
        research_title = get_accepted_research_title.research_title
    except:
       pass
    
    get_student_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id)

    get_present_panel = ProposalDefenseForm.objects.all().filter(student_leader_username=id)
    get_absent_panel = ProposalPanelInvitation.objects.all().filter(student_leader_username=id, panel_attendance = "absent")

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
        "student_leader_data": get_student_leader_data, 
        "student_leader_full_name": student_leader_full_name, 
        "group_members": get_student_group_members,
        "present_panel": get_present_panel,
        "absent_panel":get_absent_panel,

        "research_title": research_title, 
        "get_accepted_research_title":get_accepted_research_title,
        }

    return render(request, "subject-teacher-bet3-research-proposal-defense-data.html", context)
##### SUBJECT TEACHER - BET-3 - PROPOSAL DEFENSE #####

# Subject Teacher - Research Proposal Defense Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
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

# SUBJECT TEACHER - FINAL DEFENSE OPTIONS

# Subject Teacher - Set Research Final Defense Schedule Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherSetResearchFinalDefenseSchedule(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        course_available_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form = "Research Final Defense", course=course_input, status="Available")
        course_reserved_defense_schedules = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form = "Research Final Defense", course=course_input, status="Reserved")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
            "course_handled_list": course_handled_list, 
            "course_available_defense_schedules": course_available_defense_schedules, 
            "course_reserved_defense_schedules": course_reserved_defense_schedules,
            }

        return render(request, "subject-teacher-set-research-final-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-final-defense.html", context)


# Subject Teacher - BET-3 Research Final Defense Form - Save Schedule
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherSaveResearchFinalDefenseSchedule(request):
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

            return render(request, "subject-teacher-set-research-final-defense.html", context)

        if time_input not in defense_time_list:

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name, 
                "course_handled_list": course_handled_list, 
                "response": "sweet invalid defense time"}

            return render(request, "subject-teacher-set-research-final-defense.html", context)

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

            return render(request, "subject-teacher-set-research-final-defense.html", context)

        except:
            print("do not exist")
            pass

        defense_schedule = DefenseSchedule(
            username=currently_loggedin_user.username, 
            name=currently_loggedin_user_full_name, 
            course=course_input, form="Research Final Defense", 
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

        return render(request, "subject-teacher-set-research-final-defense.html", context)

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-set-research-final-defense.html", context)


# Subject Teacher - Delete Research Proposal Defense Schedule
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherDeleteResearchFinalDefenseSchedule(request, id):
    currently_loggedin_user = request.user

    delete_date = DefenseSchedule.objects.filter(username=currently_loggedin_user.username, id=id, status="Available")
    print(delete_date)

    if not delete_date:
        context = {"response": "sweet schedule not found"}

        return render(request, "subject-teacher-set-research-final-defense.html", context)

    else:
        delete_date.delete()

        context = {"response": "schedule deleted"}

        return render(request, "subject-teacher-set-research-final-defense.html", context)


# Subject Teacher - Research Final Defense Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherMyFinalDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Final Defense", course=course_input, status="Reserved")

            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
            }

            return render(request, "subject-teacher-final-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-final-defense-schedule-dashboard.html", context)


# Subject Teacher - Research Final Defense Dashboard Page
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherStudentsFinalDefenseDashboard(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    course_handled_list_unfiltered = []

    course_handled = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username)

    for course in course_handled:
        course_handled_list_unfiltered.append(course.course_major_abbr)

    course_handled_list = list(dict.fromkeys(course_handled_list_unfiltered))
    print(course_handled_list)

    if request.method == "POST":
        course_input = request.POST.get("course_input")
        print(course_input)

        try:
            student_defense_scheduled = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, course=course_input, form = "Research Final Defense", status="Reserved")
            student_defense_unscheduled = StudentLeader.objects.all().filter(bet5_subject_teacher_username=currently_loggedin_user.username, course_major_abbr=course_input, research_final_defense_date="")

            print(student_defense_unscheduled)
            context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "course_handled_list": course_handled_list,
                "student_defense_scheduled": student_defense_scheduled,
                "student_defense_unscheduled": student_defense_unscheduled,
            }

            return render(request, "subject-teacher-students-final-defense-schedule-dashboard.html", context)

        except:
            pass

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "course_handled_list": course_handled_list,
    }

    return render(request, "subject-teacher-students-final-defense-schedule-dashboard.html", context)



@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherAcknowledgementReceipt(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_receipt = AcknowledgementReceipt.objects.all().filter(subject_teacher_username = currently_loggedin_user.username, subject_teacher_response ="pending")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "pending_receipt": get_pending_receipt,
    }

    return render(request, "subject-teacher-acknowledgement-receipt.html", context)



@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherAcknowledgementReceiptAcceptSignature(request, id):
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
        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(subject_teacher_username = currently_loggedin_user.username ,subject_teacher_response ="pending")

        context = {
            "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
            "date_today": date_today,
            "pending_receipt": get_pending_receipt,
            "response": "sweet no esign",
        }

        return render(request, "subject-teacher-acknowledgement-receipt.html", context)


    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.subject_teacher_response = "Accepted"
        check_receipt.subject_teacher_response_date = date_today
        check_receipt.subject_teacher_signature = True

        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Faculty in charge) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(subject_teacher_username = currently_loggedin_user.username ,subject_teacher_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel acknowledgement receipt accepted",
            }

        return render(request, "subject-teacher-acknowledgement-receipt.html", context)

    except:
        return redirect("subject-teacher-acknowledgement-receipt")


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherAcknowledgementReceiptAccept(request, id):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    try:
        check_receipt = AcknowledgementReceipt.objects.get(id=id)

        check_receipt.subject_teacher_response = "Accepted"
        check_receipt.subject_teacher_response_date = date_today
        check_receipt.save()


        # Send g-mail notifications
        send_mail(
            "Acknowledgement Receipt",
            "Good Day " + check_receipt.student_leader_full_name + ",\n" + currently_loggedin_user_full_name + "(Faculty in charge) has accepted your Acknowledgement Receipt. \nThank you and Have a nice day. \n https://www.ditresearchdefense.online/login",
            "unofficial.tupc.uitc@gmail.com",
            ['johnanthony.bataller@gsfe.tupcavite.edu.ph'],
            fail_silently=False,

        )

        get_pending_receipt = AcknowledgementReceipt.objects.all().filter(subject_teacher_username = currently_loggedin_user.username ,subject_teacher_response ="pending")

        context = {
                "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
                "date_today": date_today,
                "pending_receipt": get_pending_receipt,
                "accepted_student_member_name": check_receipt.student_leader_full_name,
                "accepted_student_member_username": check_receipt.student_leader_username,
                "response": "sweet panel acknowledgement receipt accepted",
            }

        return render(request, "subject-teacher-acknowledgement-receipt.html", context)

    except:
        return redirect("subject-teacher-acknowledgement-receipt")


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherAcknowledgementReceiptLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_pending_receipt = AcknowledgementReceipt.objects.all().filter(subject_teacher_username = currently_loggedin_user.username, subject_teacher_response ="Accepted")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "date_today": date_today,
        "accepted_receipt": get_pending_receipt,
    }

    return render(request, "subject-teacher-acknowledgement-logs.html", context)

# Subject Teacher - BET-3 Research Title Defense Logs Dashboard
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET5FinalDefenseLogs(request):
    currently_loggedin_user = request.user

    topbar_data = topbarProcess(request)
    currently_loggedin_user_full_name = topbar_data[0]
    currently_loggedin_user_account = topbar_data[1]

    get_completed_defense_schedule = DefenseSchedule.objects.all().filter(username=currently_loggedin_user.username, form="Research Final Defense", status="Completed")
    get_redefense_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Final Defense", status="Re-Defense")
    get_reschedule_defense_schedule = DefenseScheduleLog.objects.all().filter(username=currently_loggedin_user.username, form="Research Final Defense",status="Reschedule")

    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "completed_defense_schedule": get_completed_defense_schedule,
        "redefense_defense_schedule": get_redefense_defense_schedule,
        "reschedule_defense_schedule": get_reschedule_defense_schedule,
    }

    return render(request, "subject-teacher-bet5-research-final-defense-logs.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherBET3FinalDefenseLogCompleted(request, id):

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

    if get_student_leader_data.middle_name == "":
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name
    else:
        student_leader_full_name = get_student_leader_data.last_name + " " + get_student_leader_data.suffix + ", " + get_student_leader_data.first_name + " " + get_student_leader_data.middle_name[0] + "."
    print("Student Leader Full Name: ", student_leader_full_name)
    # ----- Student Leader Data -----


    # ----- Validation ------
    
     # ----- Validation ------

    # ----- Fetch Data -----
    get_group_members = StudentGroupMember.objects.all().filter(student_leader_username=id) # Get all the group members

    get_panel_members  = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="")

    get_present_panel_members = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="present")
    get_pending_proposal_defense = FinalPanelInvitation.objects.filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="present", is_completed = False)

    get_absent_panel_members = FinalPanelInvitation.objects.all().filter(student_leader_username=id, form_status="accepted", form="Final Defense Panel Invitation", research_final_defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="absent")
    
    get_bet3_panel_invitations = FinalPanelInvitation.objects.all().filter(student_leader_username=id)

    get_proposal_defense_present_panel = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="present")

    get_present_panel_members_proposal_defense = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="present")

    get_start_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user)

    get_end_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user)

    check_pending = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user)
    
    check_pending_critique = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user)

    get_start_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, start_voting = 1)

    get_end_voting = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, start_voting = 1, end_voting = 1)

    check_pending_vote = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, final_defense_response = "")

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
        get_student_proposal_defense_schedule = DefenseSchedule.objects.get(student_leader_username=id, form="Research Final Defense", date=get_student_leader_data.research_final_defense_date, status="Reserved")
    except:
        pass
    
    try:
        get_panel_chairman = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, panel_attendance="present", is_panel_chairman=1)
        print("Panel Chairman: ", get_panel_chairman.panel_full_name)
    except:
        get_panel_chairman = None

    try:
        get_pending_panel_chairman_signature_response = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, panel_chairman_signature_response = 1)
    except:
        get_pending_panel_chairman_signature_response = 0
    
    try:
        get_done_pc_sign = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_pc_sign = None

    try:
        get_done_p_sign = FinalDefenseForm.objects.get(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, start_voting = 1, is_panel_chairman = True, panel_chairman_signature_response = True)
    except:
        get_done_p_sign = None


    all_pending_panel_signature_response = FinalDefenseForm.objects.all().filter(student_leader_username=id, defense_date=get_student_leader_data.research_final_defense_date, subject_teacher_username = request.user, start_voting = 1, panel_signature_response = False)
    
     # ----- Fetch Data -----


    context = {
        "currently_loggedin_user_full_name": currently_loggedin_user_full_name,
        "student_leader_data": get_student_leader_data,
        "student_leader_full_name": student_leader_full_name,

        "group_members": get_group_members,

        "accepted_research_title": research_title,

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
        "get_accepted_research_title_data": get_accepted_research_title,
    }

    return render(request, "subject-teacher-bet5-final-defense-data.html", context)

# Subject Teacher
@login_required(login_url="login")
@user_passes_test(lambda u: u.is_subject_teacher, login_url="login")
def subjectTeacherTheDevs(request):
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

    return render(request, "subject-teacher-the-devs.html", context)


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
