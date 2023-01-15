from django.db import models
from django.contrib.auth.models import AbstractUser

# User Account
class User(AbstractUser):
    email = models.EmailField(unique=True)
    user_account = models.CharField(max_length=256, blank=True)
    department = models.CharField(max_length=256, blank=True)

    honorific = models.CharField(max_length=256, blank=True)
    middle_name = models.CharField(max_length=256, blank=True)
    suffix = models.CharField(max_length=256, blank=True)

    is_user = models.BooleanField(default=True)

    is_administrator = models.BooleanField(default=False)

    is_department_head = models.BooleanField(default=False)

    is_panel = models.BooleanField(default=False)
    is_adviser = models.BooleanField(default=False)
    is_subject_teacher = models.BooleanField(default=False)

    is_academic_affairs = models.BooleanField(default=False)

    is_library = models.BooleanField(default=False)

    is_research_extension = models.BooleanField(default=False)

    is_student = models.BooleanField(default=False)

    is_faculty_member = models.BooleanField(default=False)

    advisee_count = models.IntegerField(default=0)
    advisee_limit = models.IntegerField(default=0)

    e_signature = models.ImageField(null=True, blank=True, upload_to = "static/signatures/")

    USERNAME_FIELD = 'username'


# Course - Major - Course Major Abbreviation
class StudentCourseMajor(models.Model):
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.course_major_abbr



class ForgotPassword(models.Model):
    username = models.CharField(max_length=256)
    token = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.username

# Student Leaders
class StudentLeader(models.Model):
    username = models.CharField(unique=True, max_length=256,)
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=256, blank=False)
    middle_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=False)
    suffix = models.CharField(max_length=256, blank=True)

    department = models.CharField(max_length=256, blank=False)
    course = models.CharField(max_length=256, blank=False)
    major = models.CharField(max_length=256, blank=False)
    course_major_abbr = models.CharField(max_length=256, blank=False)

    group_count = models.IntegerField()

    bet3_subject_teacher_username = models.CharField(max_length=256, blank=False)
    bet3_subject_teacher_name = models.CharField(max_length=256, blank=False)
    bet3_status = models.CharField(max_length=256, blank=False)

    bet5_subject_teacher_username = models.CharField(max_length=256, blank=True)
    bet5_subject_teacher_name = models.CharField(max_length=256, blank=True)
    bet5_status = models.CharField(max_length=256, blank=True)

    adviser_username = models.CharField(max_length=256, blank=True)
    adviser_name = models.CharField(max_length=256, blank=True)

    current_subject = models.CharField(max_length=256, blank=False)

    defense_status = models.CharField(max_length=256, blank=True)

    research_title_defense_date = models.CharField(max_length=256, blank=True)
    research_title_defense_start_time = models.CharField(max_length=256, blank=True)
    research_title_defense_end_time = models.CharField(max_length=256, blank=True)

    research_proposal_defense_date = models.CharField(max_length=256, blank=True)
    research_proposal_defense_start_time = models.CharField(max_length=256, blank=True)
    research_proposal_defense_end_time = models.CharField(max_length=256, blank=True)

    research_final_defense_date = models.CharField(max_length=256, blank=True)
    research_final_defense_start_time = models.CharField(max_length=256, blank=True)
    research_final_defense_end_time = models.CharField(max_length=256, blank=True)

    group_members_status = models.CharField(max_length=256, blank=True)
    research_titles_status = models.CharField(max_length=256, blank=True)
    
    bet3_panel_invitation_status = models.CharField(max_length=256, blank=True)
    title_defense_status = models.CharField(max_length=256, blank=True)

    adviser_conforme_status = models.CharField(max_length=256, blank=True)

    bet3_proposal_defense_panel_invitation_status = models.CharField(max_length=256, blank=True)
    bet3_proposal_defense_status = models.CharField(max_length=256, blank=True)

    bet5_final_defense_panel_invitation_status = models.CharField(max_length=256, blank=True)
    bet5_final_defense_status = models.CharField(max_length=256, blank=True)

    topic_panel_conforme = models.CharField(max_length=256, blank=True)
    proposal_panel_conforme = models.CharField(max_length=256, blank=True)
    final_panel_conforme = models.CharField(max_length=256, blank=True)

    acknowledgement_receipt = models.CharField(max_length=256, blank=True)

    request_limit = models.IntegerField(blank=True)

    def __str__(self) -> str:
        return self.username


# Student Group Member
class StudentGroupMember(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    student_member_username = models.CharField(max_length=256)
    student_member_full_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username


# Research Title
class ResearchTitle(models.Model):
    research_title = models.CharField(max_length=256)

    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)

    status = models.CharField(max_length=256)
    date_submitted = models.CharField(max_length=256)

    accepted = models.IntegerField(default=0)
    deferred = models.IntegerField(default=0)
    revise_title = models.IntegerField(default=0)
    suggested_title =  models.CharField(max_length=256, blank=True)
    old_research_title = models.CharField(max_length=256, blank=True)

    title_defense_status = models.CharField(max_length=256, blank=True)
    proposal_defense_status = models.CharField(max_length=256, blank=True)
    final_defense_status = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.research_title


# Research Title Logs
class ResearchTitleLog(models.Model):
    research_title = models.CharField(max_length=256)

    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)

    status = models.CharField(max_length=256)
    date_submitted = models.CharField(max_length=256)

    accepted = models.IntegerField(default=0)
    deferred = models.IntegerField(default=0)
    revise_title = models.IntegerField(default=0)
    suggested_title =  models.CharField(max_length=256, blank=True)
    old_research_title = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)

    title_defense_status = models.CharField(max_length=256, blank=True)
    proposal_defense_status = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.research_title


# Defense Schedule
class DefenseSchedule(models.Model):
    username = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)
    form = models.CharField(max_length=256)
    date = models.CharField(max_length=256)
    start_time = models.CharField(max_length=256)
    end_time = models.CharField(max_length=256)
    status = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.username


# Defense Schedule Logs
class DefenseScheduleLog(models.Model):
    username = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)
    form = models.CharField(max_length=256)
    date = models.CharField(max_length=256)
    start_time = models.CharField(max_length=256)
    end_time = models.CharField(max_length=256)
    status = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.username


class FilePath(models.Model):
    student_leader_username = models.CharField(max_length=256)
    file_path = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username


##### TITLE DEFENSE #####

# BET-3 - Title Defense  - Panel Invitation
class TitlePanelInvitation(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_title_defense_date = models.CharField(max_length=256, blank=True)
    research_title_defense_start_time = models.CharField(max_length=256, blank=True)
    research_title_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Title Defense Form
class TitleDefenseForm(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    is_panel_chairman = models.BooleanField(default=False)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    start_voting = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)
    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Title Voting
class TitleVote(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    research_title = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Title Defense - Panel Invitation - Logs
class TitlePanelInvitationLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_title_defense_date = models.CharField(max_length=256, blank=True)
    research_title_defense_start_time = models.CharField(max_length=256, blank=True)
    research_title_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Title Defense Form - Logs
class TitleDefenseFormLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    is_panel_chairman = models.BooleanField(default=False)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)
    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


##### ADVISER CONFORME #####

# BET-3 Adviser Conforme
class AdviserConforme(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)

    research_title = models.CharField(max_length=256, blank=True)

    form_date_submitted = models.CharField(max_length=256)

    dit_head_username = models.CharField(max_length=256)
    dit_head_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    adviser_username = models.CharField(max_length=256)
    adviser_name = models.CharField(max_length=256)
    adviser_response = models.CharField(max_length=256)
    adviser_response_date = models.CharField(max_length=256)
    adviser_signature = models.BooleanField(default=False)
    form_status = models.CharField(max_length=256)

    adviser_response_date_exp = models.CharField(max_length=256, blank=True)

    thesis_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 Research Adviser Conforme Logs
class AdviserConformeLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)

    research_title = models.CharField(max_length=256, blank=True)

    form_date_submitted = models.CharField(max_length=256)

    dit_head_username = models.CharField(max_length=256)
    dit_head_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    adviser_username = models.CharField(max_length=256)
    adviser_name = models.CharField(max_length=256)
    adviser_response = models.CharField(max_length=256)
    adviser_response_date = models.CharField(max_length=256)
    adviser_signature = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    thesis_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


##### PROPOSAL DEFENSE #####

#  BET-3 - Proposal Defense - Panel Invitation
class ProposalPanelInvitation(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_proposal_defense_date = models.CharField(max_length=256, blank=True)
    research_proposal_defense_start_time = models.CharField(max_length=256, blank=True)
    research_proposal_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


#  BET-3 - Proposal Defense - Panel Invitation - Logs
class ProposalPanelInvitationLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_proposal_defense_date = models.CharField(max_length=256, blank=True)
    research_proposal_defense_start_time = models.CharField(max_length=256, blank=True)
    research_proposal_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Proposal Defense Critique Form
class ProposalDefenseCritique(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    is_panel_chairman = models.BooleanField(default=False)
    panel_chairman_signature_response = models.BooleanField(default=False)
    panel_chairman_signature_attach = models.BooleanField(default=False)  

    form_date = models.CharField(max_length=256)

    critique = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    research_title = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 -  Proposal Defense Form
class ProposalDefenseForm(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    is_panel_chairman = models.BooleanField(default=False)
    panel_chairman_signature_response = models.BooleanField(default=False)
    panel_chairman_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    start_critique = models.BooleanField(default=False)
    end_critique = models.BooleanField(default=False)

    start_voting = models.BooleanField(default=False)
    end_voting = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    critique_sign_response = models.BooleanField(default=False)
    proposal_defense_response = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-3 - Proposal Defense Form - Log
class ProposalDefenseFormLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    is_panel_chairman = models.BooleanField(default=False)
    panel_chairman_signature_response = models.BooleanField(default=False)
    panel_chairman_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    start_critique = models.BooleanField(default=False)
    end_critique = models.BooleanField(default=False)

    start_voting = models.BooleanField(default=False)
    end_voting = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    critique_sign_response = models.BooleanField(default=False)
    proposal_defense_response = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


##### Final DEFENSE #####

#  BET-5 - Final Defense - Panel Invitation
class FinalPanelInvitation(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_final_defense_date = models.CharField(max_length=256, blank=True)
    research_final_defense_start_time = models.CharField(max_length=256, blank=True)
    research_final_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


#  BET-5 - Final Defense - Panel Invitation - Logs
class FinalPanelInvitationLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)
    panel_attendance = models.CharField(max_length=256, blank=True)

    research_final_defense_date = models.CharField(max_length=256, blank=True)
    research_final_defense_start_time = models.CharField(max_length=256, blank=True)
    research_final_defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-5 -  Final Defense Form
class FinalDefenseForm(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    is_panel_chairman = models.BooleanField(default=False)
    panel_chairman_signature_response = models.BooleanField(default=False)
    panel_chairman_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    start_voting = models.BooleanField(default=False)
    end_voting = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    final_defense_response = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


# BET-5 - Final Defense Form - Log
class FinalDefenseFormLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    panel_signature_response = models.BooleanField(default=False)
    panel_signature_attach = models.BooleanField(default=False)

    is_panel_chairman = models.BooleanField(default=False)
    panel_chairman_signature_response = models.BooleanField(default=False)
    panel_chairman_signature_attach = models.BooleanField(default=False)

    form_date = models.CharField(max_length=256)

    start_voting = models.BooleanField(default=False)
    end_voting = models.BooleanField(default=False)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    final_defense_response = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.student_leader_username


# Panel Conforme
class PanelConforme(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)

    research_title = models.CharField(max_length=256, blank=True)
    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# Panel Conforme
class PanelConformeLog(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
    panel_signature = models.BooleanField(default=False)

    research_title = models.CharField(max_length=256, blank=True)
    defense_date = models.CharField(max_length=256, blank=True)
    defense_start_time = models.CharField(max_length=256, blank=True)
    defense_end_time = models.CharField(max_length=256, blank=True)

    form_date_sent = models.CharField(max_length=256)
    form_status = models.CharField(max_length=256)
    form = models.CharField(max_length=256)

    subject_teacher_username = models.CharField(max_length=256, blank=True)
    subject_teacher_full_name = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username


# Acknowledgement Receipt
class AcknowledgementReceipt(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)
    dit_head_signature = models.BooleanField(default=False)

    adaa_username = models.CharField(max_length=256)
    adaa_full_name = models.CharField(max_length=256)
    adaa_response = models.CharField(max_length=256)
    adaa_response_date = models.CharField(max_length=256)
    adaa_signature = models.BooleanField(default=False)

    library_username = models.CharField(max_length=256)
    library_full_name = models.CharField(max_length=256)
    library_response = models.CharField(max_length=256)
    library_response_date = models.CharField(max_length=256)
    library_signature = models.BooleanField(default=False)

    research_ext_username = models.CharField(max_length=256)
    research_ext_full_name = models.CharField(max_length=256)
    research_ext_response = models.CharField(max_length=256)
    research_ext_response_date = models.CharField(max_length=256)
    research_ext_signature = models.BooleanField(default=False)

    adviser_username = models.CharField(max_length=256)
    adviser_full_name = models.CharField(max_length=256)
    adviser_response = models.CharField(max_length=256)
    adviser_response_date = models.CharField(max_length=256)
    adviser_signature = models.BooleanField(default=False)

    subject_teacher_username = models.CharField(max_length=256)
    subject_teacher_full_name = models.CharField(max_length=256)
    subject_teacher_response = models.CharField(max_length=256)
    subject_teacher_response_date = models.CharField(max_length=256)
    subject_teacher_signature = models.BooleanField(default=False)

    research_title = models.CharField(max_length=256, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student_leader_username

