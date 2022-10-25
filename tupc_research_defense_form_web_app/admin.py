from django.contrib import admin
from .models import *

admin.site.register(User)

admin.site.register(StudentCourseMajor)
admin.site.register(StudentLeader)
admin.site.register(StudentGroupMember)
admin.site.register(ResearchTitle)

admin.site.register(DefenseSchedule)

admin.site.register(BET3PanelInvitation)
admin.site.register(BET3ResearchTitleDefenseForm)
admin.site.register(BET3ResearchTitleVote)
admin.site.register(BET3AdviserConforme)

admin.site.register(FilePath)

admin.site.register(DefenseScheduleLog)
admin.site.register(BET3PanelInvitationLog)
admin.site.register(BET3ResearchTitleDefenseFormLog)
admin.site.register(BET3AdviserConformeLog)
