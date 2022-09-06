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

    USERNAME_FIELD = 'username'


# Course - Major - Course Major Abbreviation
class StudentCourseMajor(models.Model):
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.course_major_abbr

# Student Leaders
class StudentLeader(models.Model):
    username = models.EmailField(unique=True)
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

    bet3_subject_teacher_username = models.CharField(
        max_length=256, blank=False)
    bet3_subject_teacher_name = models.CharField(max_length=256, blank=False)
    bet3_status = models.CharField(max_length=256, blank=False)

    bet5_subject_teacher_username = models.CharField(
        max_length=256, blank=True)
    bet5_subject_teacher_name = models.CharField(max_length=256, blank=True)
    bet5_status = models.CharField(max_length=256, blank=True)

    current_subject = models.CharField(max_length=256, blank=False)

    defense_status = models.CharField(max_length=256, blank=True)

    defense_status = models.CharField(max_length=256, blank=True)

    research_title_defense_date = models.CharField(max_length=256, blank=True)
    research_title_defense_start_time = models.CharField(max_length=256, blank=True)
    research_title_defense_end_time = models.CharField(max_length=256, blank=True)

    group_members_status = models.CharField(max_length=256, blank=True)
    research_titles_status = models.CharField(max_length=256, blank=True)
    bet3_panel_invitation_status = models.CharField(max_length=256, blank=True)
    title_defense_status = models.CharField(max_length=256, blank=True)

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

# Panel Invitation - BET-3
class BET3PanelInvitation(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)
    
    dit_head_username= models.CharField(max_length=256)
    dit_head_full_name = models.CharField(max_length=256)
    dit_head_response = models.CharField(max_length=256)
    dit_head_response_date = models.CharField(max_length=256)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_response = models.CharField(max_length=256)
    panel_response_date = models.CharField(max_length=256)
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

# Research Title Defense - BET-3
class BET3ResearchTitleDefenseForm(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_full_name = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256, blank=True)

    panel_username = models.CharField(max_length=256)
    panel_full_name = models.CharField(max_length=256)
    panel_attendance = models.CharField(max_length=256)
    is_panel_chairman = models.BooleanField(default=False)

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

# Research Title Vote - BET-3
class BET3ResearchTitleVote(models.Model):
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


class FilePath(models.Model):
    student_leader_username = models.CharField(max_length=256)
    file_path = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username


# class PanelInvitationBET3Declined(models.Model):
#     student_leader_username = models.CharField(max_length=256)

#     dit_head_name = models.CharField(max_length=256)
#     dit_head_response = models.CharField(max_length=256)
#     dit_head_response_date = models.CharField(max_length=256)

#     panel_member_username = models.CharField(max_length=256)
#     panel_member_name = models.CharField(max_length=256)
#     panel_member_response = models.CharField(max_length=256)
#     panel_member_response_date = models.CharField(max_length=256)

#     student_member_username_1 = models.CharField(max_length=256)
#     student_member_name_1 = models.CharField(max_length=256)

#     student_member_username_2 = models.CharField(max_length=256)
#     student_member_name_2 = models.CharField(max_length=256)

#     student_member_username_3 = models.CharField(max_length=256)
#     student_member_name_3 = models.CharField(max_length=256)

#     student_member_username_4 = models.CharField(max_length=256)
#     student_member_name_4 = models.CharField(max_length=256)

#     student_member_username_5 = models.CharField(max_length=256)
#     student_member_name_5 = models.CharField(max_length=256)

#     course = models.CharField(max_length=256)
#     major = models.CharField(max_length=256)
#     course_major_abbr = models.CharField(max_length=256)

#     research_title_1 = models.CharField(max_length=256)
#     research_title_2 = models.CharField(max_length=256)
#     research_title_3 = models.CharField(max_length=256)
#     research_title_4 = models.CharField(max_length=256)
#     research_title_5 = models.CharField(max_length=256)

#     form_date_submitted = models.CharField(max_length=256)
#     defense_date = models.CharField(max_length=256)
#     defense_start_time = models.CharField(max_length=256)
#     defense_end_time = models.CharField(max_length=256)

#     form = models.CharField(max_length=256)

#     def __str__(self) -> str:
#         return self.student_leader_username


# Panel Conforme - BET-3
# class PanelConformeBET3(models.Model):
#     student_leader_username = models.CharField(max_length=256)

#     dept_head = models.CharField(max_length=256)
#     dept_head_status = models.CharField(max_length=256)

#     panel_member_1 = models.CharField(max_length=256)
#     panel_member_2 = models.CharField(max_length=256)
#     panel_member_3 = models.CharField(max_length=256)
#     panel_member_4 = models.CharField(max_length=256)
#     panel_member_5 = models.CharField(max_length=256)

#     panel_member_name_1 = models.CharField(max_length=256)
#     panel_member_name_2 = models.CharField(max_length=256)
#     panel_member_name_3 = models.CharField(max_length=256)
#     panel_member_name_4 = models.CharField(max_length=256)
#     panel_member_name_5 = models.CharField(max_length=256)

#     panel_member_status_1 = models.CharField(max_length=256)
#     panel_member_status_2 = models.CharField(max_length=256)
#     panel_member_status_3 = models.CharField(max_length=256)
#     panel_member_status_4 = models.CharField(max_length=256)
#     panel_member_status_5 = models.CharField(max_length=256)

#     student_member_1 = models.CharField(max_length=256)
#     student_member_2 = models.CharField(max_length=256)
#     student_member_3 = models.CharField(max_length=256)
#     student_member_4 = models.CharField(max_length=256)
#     student_member_5 = models.CharField(max_length=256)

#     student_member_username_1 = models.CharField(max_length=256)
#     student_member_username_2 = models.CharField(max_length=256)
#     student_member_username_3 = models.CharField(max_length=256)
#     student_member_username_4 = models.CharField(max_length=256)
#     student_member_username_5 = models.CharField(max_length=256)

#     course = models.CharField(max_length=256)
#     major = models.CharField(max_length=256)
#     course_major_abbr = models.CharField(max_length=256)

#     research_title = models.CharField(max_length=256)

#     date_submitted = models.CharField(max_length=256)

#     form_status = models.CharField(max_length=256)

#     def __str__(self) -> str:
#         return self.student_leader_username





