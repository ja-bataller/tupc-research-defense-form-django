from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(StudentGroupMember)
admin.site.register(ResearchTitle)
admin.site.register(PanelConformeBET3)
admin.site.register(StudentCourseMajor)