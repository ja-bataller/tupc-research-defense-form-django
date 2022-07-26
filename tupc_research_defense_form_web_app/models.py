from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom - Creating User Account
class User(AbstractUser):
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=256, blank=True)
    major = models.CharField(max_length=256, blank=True)
    department = models.CharField(max_length=256, blank=True)

    middle_name = models.CharField(max_length=256, blank=True)

    is_user = models.BooleanField(default=True)
    is_administrator = models.BooleanField(default=False)
    is_department_head = models.BooleanField(default=False)
    is_panel = models.BooleanField(default=False)
    is_adviser = models.BooleanField(default=False)
    is_subject_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    # is_superuser = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=True)
    # is_developer = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

####################################################################################################################

class StudentCourseMajor(models.Model):
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    course_major_abbr = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.course_major_abbr