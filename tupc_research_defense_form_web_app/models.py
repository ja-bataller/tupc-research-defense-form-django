from django.db import models
from django.contrib.auth.models import AbstractUser

# User Account
class User(AbstractUser):
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=256, blank=True)
    department = models.CharField(max_length=256, blank=True)

    honorific = models.CharField(max_length=256, blank=True)
    middle_name = models.CharField(max_length=256, blank=True)

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

    # is_superuser = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=True)
    # is_developer = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

####################################################################################################################

# Course - Major - Course Major Abbreviation
class StudentCourseMajor(models.Model):
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.course_major_abbr
    
####################################################################################################################

# Panel Conforme - BET-3
class PanelConformeBET3(models.Model):
    student_leader_username = models.CharField(max_length=256)

    dept_head = models.CharField(max_length=256)
    dept_head_status = models.CharField(max_length=256)

    panel_member_1 = models.CharField(max_length=256)
    panel_member_2 = models.CharField(max_length=256)
    panel_member_3 = models.CharField(max_length=256)
    panel_member_4 = models.CharField(max_length=256)
    panel_member_5 = models.CharField(max_length=256)

    panel_member_name_1 = models.CharField(max_length=256)
    panel_member_name_2 = models.CharField(max_length=256)
    panel_member_name_3 = models.CharField(max_length=256)
    panel_member_name_4 = models.CharField(max_length=256)
    panel_member_name_5 = models.CharField(max_length=256)

    panel_member_status_1 = models.CharField(max_length=256)
    panel_member_status_2 = models.CharField(max_length=256)
    panel_member_status_3 = models.CharField(max_length=256)
    panel_member_status_4 = models.CharField(max_length=256)
    panel_member_status_5 = models.CharField(max_length=256)

    student_member_1 = models.CharField(max_length=256)
    student_member_2 = models.CharField(max_length=256)
    student_member_3 = models.CharField(max_length=256)
    student_member_4 = models.CharField(max_length=256)
    student_member_5 = models.CharField(max_length=256)

    student_member_username_1 = models.CharField(max_length=256)
    student_member_username_2 = models.CharField(max_length=256)
    student_member_username_3 = models.CharField(max_length=256)
    student_member_username_4 = models.CharField(max_length=256)
    student_member_username_5 = models.CharField(max_length=256)

    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    research_title = models.CharField(max_length=256)

    date_submitted = models.CharField(max_length=256)

    form_status = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username

####################################################################################################################

# Research Title
class ResearchTitle(models.Model):
    research_title = models.CharField(max_length=256)
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)
    status = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)
    date_submitted = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.research_title

####################################################################################################################

# Student Group Members
class StudentGroupMembers(models.Model):
    student_leader_username = models.CharField(max_length=256)
    student_leader_name = models.CharField(max_length=256)
    student_member_username = models.CharField(max_length=256)
    student_member_name = models.CharField(max_length=256)
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.student_leader_username