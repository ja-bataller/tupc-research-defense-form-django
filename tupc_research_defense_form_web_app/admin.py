from django.contrib import admin
from .models import *

admin.site.register(User)

admin.site.register(StudentCourseMajor)
admin.site.register(StudentLeader)
admin.site.register(StudentGroupMember)
admin.site.register(ResearchTitle)

admin.site.register(DefenseSchedule)

admin.site.register(TitlePanelInvitation)
admin.site.register(TitleDefenseForm)
admin.site.register(TitleVote)
admin.site.register(AdviserConforme)

admin.site.register(FilePath)

admin.site.register(DefenseScheduleLog)
admin.site.register(TitlePanelInvitationLog)
admin.site.register(TitleDefenseFormLog)
admin.site.register(AdviserConformeLog)
